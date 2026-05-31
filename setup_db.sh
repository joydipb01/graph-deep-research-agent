#!/bin/bash

# Quick setup script for PostgreSQL with pgvector
# Uses Docker (v2 compose) or Podman

set -e

echo "Setting up PostgreSQL database for graph-deep-research-agent..."

# Check if .env exists, create from template if not
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your actual API keys"
fi

# Check for available container runtime
if docker compose version &>/dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v podman-compose &>/dev/null; then
    COMPOSE_CMD="podman-compose"
else
    echo "✗ Neither 'docker compose' nor 'podman-compose' found."
    echo ""
    echo "Please install one of the following:"
    echo "  - Docker Compose v2: https://docs.docker.com/compose/install/"
    echo "  - Podman Compose: pip install podman-compose"
    echo ""
    echo "Alternatively, set up PostgreSQL manually (see SETUP_DATABASE.md)"
    exit 1
fi

echo "Using: $COMPOSE_CMD"

# Start PostgreSQL container
echo "Starting PostgreSQL container..."
$COMPOSE_CMD up -d postgres

# Wait for database to be ready
echo "Waiting for database to be ready..."
while true; do
    if docker exec graph-research-postgres pg_isready -U postgres 2>/dev/null; then
        echo "✓ Database is ready!"
        break
    else
        echo "  Waiting..."
        sleep 2
    fi
done

# Initialize pgvector extension and create tables
echo "Initializing pgvector extension and creating tables..."
docker exec graph-research-postgres psql -U postgres -d graph_research -c "
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS research_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    url TEXT,
    source_type TEXT,
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_research_embedding ON research_documents USING ivfflat (embedding vector_l2_ops);

CREATE TABLE IF NOT EXISTS research_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES research_sessions(id),
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS graph_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_type TEXT NOT NULL,
    label TEXT NOT NULL,
    properties JSONB,
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS graph_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_node_id UUID REFERENCES graph_nodes(id),
    target_node_id UUID REFERENCES graph_nodes(id),
    relationship_type TEXT NOT NULL,
    weight FLOAT DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_embedding ON graph_nodes USING ivfflat (embedding vector_l2_ops);
"

echo "✓ Database setup complete!"
echo ""
echo "Connection details:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: graph_research"
echo "  User: postgres"
echo ""
echo "To connect: psql -U postgres -d graph_research -h localhost"
echo "To stop: $COMPOSE_CMD down"