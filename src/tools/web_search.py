import os
from typing import Annotated, Literal
from langchain.tools import InjectedToolArg, tool
from tavily import AsyncTavilyClient

from dotenv import load_dotenv
from src.utils.tasks import fetch_webpage_content

load_dotenv()

tavily_client = AsyncTavilyClient(os.environ["TAVILY_API_KEY"])

@tool(parse_docstring=True)
async def tavily_search(
    query: str,
    topic: Annotated[
        Literal["general", "news", "finance"], InjectedToolArg
    ],
    max_results: Annotated[int, InjectedToolArg] = 3,
) -> str:
    """Search the web for information on a given query.

    Uses Tavily to discover relevant URLs, then fetches and returns full webpage content as markdown.

    Args:
        query: Search query to execute
        topic: Topic filter - 'general', 'news', or 'finance'. Use 'general' for broad searches, 'news' for current events, and 'finance' for financial topics.
        max_results: Maximum number of results to return (default: 3)

    Returns:
        Formatted search results with full webpage content
    """
    try:
        search_results = await tavily_client.search(
            query,
            max_results=max_results,
            topic=topic,
        )
        result_texts = []
        for result in search_results.get("results", []):
            url = result["url"]
            title = result["title"]
            content = await fetch_webpage_content(url)
            result_texts.append(f"## {title}\n**URL:** {url}\n\n{content}\n---")

        return f"Found {len(result_texts)} result(s) for '{query}':\n\n" + "\n".join(
            result_texts
        )
    
    except Exception as e:
        return f"Error during Tavily search: {e}"