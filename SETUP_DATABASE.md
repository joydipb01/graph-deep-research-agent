# PostgreSQL with pgvector Setup Guide

This guide explains how to set up PostgreSQL with the pgvector extension for the graph-deep-research-agent.

## Option 1: Docker Setup (Recommended)

The quickest way to get started for development:

### 1. Start the database

```bash
# Start the PostgreSQL container with pgvector
docker-compose up -d postgres

# Wait for the database to be ready (check logs)
docker-compose logs -f postgres
```

### 2. Initialize the database schema

```bash
# Run the setup script
docker-compose exec postgres psql -U postgres -d graph_research -f /path/to/database_setup.sql

# Or connect and run manually
docker-compose exec postgres psql -U postgres -d graph_research
```

Then in the psql prompt:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### 3. Update your .env file

Copy the example and fill in your values:
```bash
cp .env.example .env
# Edit .env with your actual API keys and database URL
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Verify connection

```python
python -c "
from src.utils.database import get_connection_string, get_pgvector_store
print('Connection string:', get_connection_string())
# Should print your connection details
```

## Option 2: Local PostgreSQL Installation

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS (Homebrew):**
```bash
brew install postgresql
```

**Windows:**
Download from https://www.postgresql.org/download/windows/

### 2. Install pgvector extension

**Ubuntu/Debian:**
```bash
sudo apt install postgresql-15-pgvector
# Replace 15 with your PostgreSQL version
```

**macOS:**
```bash
# Using Homebrew
brew install pgvector
```

**Manual installation:**
```bash
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
make install
```

### 3. Create the database and enable extension

```bash
# Connect as postgres user
sudo -u postgres psql

# In psql:
CREATE DATABASE graph_research;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE graph_research TO postgres;
\q

# Connect to the database and enable vector extension
psql -U postgres -d graph_research -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 4. Run the schema setup

```bash
psql -U postgres -d graph_research -f database_setup.sql
```

## Option 3: Cloud PostgreSQL (Supabase, etc.)

If using a cloud provider like Supabase:

1. Create a new project
2. Enable the pgvector extension in the dashboard (SQL editor):
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Get your connection string from the project settings
4. Update `.env` with the connection string

## Quick Start Script

Run this to set up everything automatically with Docker:

```bash
# 1. Create .env from template
cp .env.example .env

# 2. Start database
docker-compose up -d postgres

# 3. Wait for it to be ready
sleep 5

# 4. Initialize schema
docker-compose exec postgres psql -U postgres -d graph_research -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 5. Install dependencies
pip install -r requirements.txt
```

## Verifying the Setup

```python
from src.utils.database import initialize_database, get_pgvector_store

# Check database connection
if initialize_database():
    print("✓ Database connection successful")
else:
    print("✗ Database connection failed")

# Test vector operations (requires embeddings)
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = get_pgvector_store(
    collection_name="test_collection",
    embeddings=embeddings
)
print("✓ PGVector store created successfully")
```

## Common Issues

### Connection refused
- Ensure PostgreSQL is running: `docker-compose ps` or `sudo service postgresql status`
- Check the connection string in `.env`

### Extension not found
- Verify pgvector is installed: `psql -c "SELECT * FROM pg_extension;"`
- Install it: `psql -c "CREATE EXTENSION vector;"`

### Permission denied
- Check user permissions in PostgreSQL
- Ensure the user has CREATE privileges on the database

## Next Steps

After setting up the database, you can:
1. Use `PGVector` for vector storage and similarity search
2. Create graph relationships between research documents
3. Store and retrieve chat history
4. Build knowledge graphs from research findings