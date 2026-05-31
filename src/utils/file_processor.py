import pymupdf4llm
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pgvector.psycopg2 import register_vector
import os
import psycopg
import asyncio

from src.utils.database import get_connection_string


async def _extract_markdown_from_pdf(pdf_path: str) -> str:
    """Extract markdown from a PDF file using pymupdf4llm."""
    md_text = pymupdf4llm.to_markdown(pdf_path)
    return md_text


async def _chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
    """Split text into chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = splitter.split_text(text)
    return chunks


async def _create_pgvector_table(conn: psycopg.Connection) -> None:
    """Create the pgvector table if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                embedding vector(1536),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_documents_embedding ON documents USING ivfflat (embedding vector_l2_ops)")
        conn.commit()


async def _get_embedding(text: str) -> list:
    """Get embedding for text using OpenAI."""
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
        model="nvidia/llama-nemotron-embed-vl-1b-v2:free",
        openai_api_base="https://openrouter.ai/api/v1",
    )
    return await embeddings.aembed_query(text)


async def _store_chunks_in_pgvector(chunks: list, pdf_name: str, conn: psycopg.Connection) -> None:
    """Store text chunks as vectors in pgvector database."""
    await _create_pgvector_table(conn)

    with conn.cursor() as cur:
        for i, chunk in enumerate(chunks):
            embedding = await _get_embedding(chunk)
            metadata = {"source": pdf_name, "chunk": i}
            cur.execute(
                "INSERT INTO documents (content, embedding, metadata) VALUES (%s, %s, %s)",
                (chunk, embedding, metadata)
            )
        conn.commit()


async def process_pdf(pdf_path: str, conn_string: str = None) -> None:
    """Complete pipeline: extract markdown, chunk, and store in pgvector."""
    if conn_string is None:
        conn_string = get_connection_string()

    # Extract markdown
    markdown = await _extract_markdown_from_pdf(pdf_path)

    # Chunk the text
    chunks = await _chunk_text(markdown)

    # Connect to database and store
    conn = psycopg.connect(conn_string)
    register_vector(conn)
    await _store_chunks_in_pgvector(chunks, os.path.basename(pdf_path), conn)
    conn.close()

    print(f"Processed {len(chunks)} chunks from {pdf_path}")
