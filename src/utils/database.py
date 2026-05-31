"""Database utilities for PostgreSQL with pgvector."""

from typing import Optional, Any
from langchain_core.embeddings import Embeddings
from langchain_postgres import PGVector
from dotenv import load_dotenv
import os

load_dotenv()


def get_connection_string() -> str:
    """Get the PostgreSQL connection string from environment."""
    connection_string = os.getenv("DATABASE_URL")
    if connection_string is None:
        connection_string = "postgresql://localhost:5432/graph_research"
    return connection_string


def get_pgvector_store(
    collection_name: str = "research_documents",
    embeddings: Optional[Embeddings] = None,
) -> PGVector:
    """
    Create a PGVector store instance.

    Args:
        collection_name: Name of the collection/table to use
        embeddings: Embedding model to use (required for storing vectors)

    Returns:
        PGVector instance for vector operations
    """
    connection_string = get_connection_string()

    return PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection_string,
        pre_delete_collection=False,
    )


async def initialize_database() -> bool:
    """
    Initialize database tables and extensions.

    Returns:
        True if initialization successful, False otherwise
    """
    import psycopg

    connection_string = get_connection_string()

    try:
        conn = psycopg.AsyncConnection.connect(connection_string)
        async with conn:
            async with conn.cursor() as cur:
                # Enable pgvector extension
                await cur.execute(
                    "CREATE EXTENSION IF NOT EXISTS vector"
                )
                await conn.commit()
        return True
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False