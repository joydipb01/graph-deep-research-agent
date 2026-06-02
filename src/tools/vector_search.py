"""Vector search tool for pgvector database similarity search."""

import os
from typing import Annotated, Any
from langchain.tools import InjectedToolArg, tool
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from src.utils.database import get_pgvector_store


@tool(parse_docstring=True)
async def vector_search(
    query: str,
    collection_name: Annotated[
        str, InjectedToolArg
    ] = "research_documents",
    k: Annotated[int, InjectedToolArg] = 5,
) -> str:
    """Search the pgvector database for similar documents using embeddings.

    Performs similarity search on stored research documents to find relevant
    content based on semantic similarity to the query.

    Args:
        query: The search query to find similar documents for.
        collection_name: Name of the collection to search in (default: research_documents).
        k: Number of similar documents to return (default: 5).

    Returns:
        Formatted search results with document content and similarity scores.
    """
    try:
        embeddings = OpenAIEmbeddings(
            model="nvidia/llama-nemotron-embed-vl-1b-v2:free",
            openai_api_base="https://openrouter.ai/api/v1",
        )
        store = get_pgvector_store(
            collection_name=collection_name,
            embeddings=embeddings,
        )

        # Perform similarity search (returns list of (Document, score) tuples)
        results: list[tuple[Document, float]] = (
            store.similarity_search_with_score(query=query, k=k)
        )

        if not results:
            msg = f"No similar documents found in '{collection_name}' for: '{query}'"
            return msg

        # Format results
        formatted_results: list[str] = []
        for i, (doc, score) in enumerate(results, 1):
            content = doc.page_content
            metadata: dict[str, Any] = doc.metadata or {}

            # Build source info from metadata
            source_parts: list[str] = []
            if source := metadata.get("source"):
                source_parts.append(str(source))
            if title := metadata.get("title"):
                source_parts.append(str(title))

            source_info = (
                " | ".join(source_parts) if source_parts else "Unknown source"
            )

            formatted_results.append(
                f"## Result {i}\n"
                f"**Source:** {source_info}\n"
                f"**Similarity Score:** {score:.4f}\n\n"
                f"{content}\n---"
            )

        return (
            f"Found {len(results)} similar document(s) in '{collection_name}' "
            f"for query: '{query}'\n\n" + "\n".join(formatted_results)
        )

    except Exception as e:
        return f"Error during vector search: {e}"