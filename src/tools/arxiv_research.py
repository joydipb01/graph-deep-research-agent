from langchain.tools import InjectedToolArg, tool
from typing import Annotated
import httpx
import feedparser

from src.utils.tasks import fetch_webpage_content

@tool(parse_docstring=True)
async def search_arxiv(
    query: str, 
    max_results: Annotated[int, InjectedToolArg] = 3
) -> list:
    """Searches arXiv for the top 3 recent papers matching the query 
    and returns their titles, URLs, and content in markdown format.

    Args:
        query: Search query to execute
        max_results: Maximum number of results to return (default: 3)

    Returns:
        Formatted search results with full paper content
    """

    url = "https://export.arxiv.org/api/query"

    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }

    headers = {
        "User-Agent": "DeepResearchAgent/1.0 email@example.com"
    }

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            feed = feedparser.parse(response.text)
            results = []
            for entry in feed.entries:
                url = entry.id.replace("abs", "html")
                title = entry.title
                content = await fetch_webpage_content(url)
                results.append(f"## {title}\n**URL:** {url}\n\n{content}\n---")
            return results
    except Exception as e:
        return f"Error searching arXiv: {e}"