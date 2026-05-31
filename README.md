# graph-deep-research-agent

A LangChain-based research agent for deep web and arXiv research with vector storage.

## Quick Setup

### 1. Set up the database

```bash
# Quick setup with Docker (recommended)
./setup_db.sh

# Or manually:
docker-compose up -d postgres
docker-compose exec postgres psql -U postgres -d graph_research -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

## Database Schema

The database includes tables for:
- `research_documents` - Store research papers and articles with embeddings
- `research_sessions` - Track research sessions
- `chat_messages` - Store conversation history
- `graph_nodes` / `graph_edges` - Knowledge graph storage

See `SETUP_DATABASE.md` for detailed setup instructions.
