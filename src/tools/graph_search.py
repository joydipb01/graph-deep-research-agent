"""Graph search tool for knowledge graph node similarity search."""

from typing import Annotated, Any, Optional
from langchain.tools import InjectedToolArg, tool
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from src.utils.database import get_pgvector_store


@tool(parse_docstring=True)
async def graph_search(
    query: str,
    k: Annotated[int, InjectedToolArg] = 5,
    node_type: Annotated[Optional[str], InjectedToolArg] = None,
) -> str:
    """Search the knowledge graph nodes for similar concepts using embeddings.

    Performs similarity search on stored graph nodes to find relevant concepts
    based on semantic similarity to the query. Returns node labels, properties,
    and optionally filters by node type.

    Args:
        query: The search query to find similar graph nodes for.
        k: Number of similar nodes to return (default: 5).
        node_type: Optional filter by node type (paper, concept, source, etc.).

    Returns:
        Formatted search results with node labels, properties, and similarity scores.
    """
    try:
        embeddings = OpenAIEmbeddings(
            model="nvidia/llama-nemotron-embed-vl-1b-v2:free",
            openai_api_base="https://openrouter.ai/api/v1",
        )
        store = get_pgvector_store(
            collection_name="graph_nodes",
            embeddings=embeddings,
        )

        # Build filter if node_type specified
        filter_dict: Optional[dict[str, Any]] = None
        if node_type:
            filter_dict = {"node_type": node_type}

        # Perform similarity search
        results: list[tuple[Document, float]] = (
            store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter_dict,
            )
        )

        if not results:
            msg = f"No similar graph nodes found for: '{query}'"
            if node_type:
                msg = f"No similar graph nodes found for '{query}' with type '{node_type}'"
            return msg

        # Format results
        formatted_results: list[str] = []
        for i, (doc, score) in enumerate(results, 1):
            content = doc.page_content
            metadata: dict[str, Any] = doc.metadata or {}

            node_type_label = metadata.get("node_type", "unknown")
            label = metadata.get("label", "Unknown")
            properties = metadata.get("properties", {})

            prop_str = ""
            if properties:
                prop_str = "\n**Properties:**\n"
                for key, value in properties.items():
                    prop_str += f"  - {key}: {value}\n"

            formatted_results.append(
                f"## Node {i}\n"
                f"**Label:** {label}\n"
                f"**Type:** {node_type_label}\n"
                f"**Similarity Score:** {score:.4f}\n"
                f"{prop_str}\n"
                f"**Content:** {content}\n---"
            )

        return (
            f"Found {len(results)} similar graph node(s) for query: '{query}'\n\n"
            + "\n".join(formatted_results)
        )

    except Exception as e:
        return f"Error during graph search: {e}"