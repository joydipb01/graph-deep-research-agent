import asyncio
import httpx
from markdownify import markdownify as md
from datetime import datetime as dt

async def fetch_webpage_content(url: str, timeout: float = 10.0) -> str:
    """Fetch webpage and convert HTML to markdown."""
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, timeout=timeout)
            response.raise_for_status()
            return md(response.text)
    except Exception as e:
        return f"Error fetching {url}: {e}"


async def get_todays_date() -> str:
    """Return today's date in YYYY-MM-DD format."""
    await asyncio.sleep(0)
    return dt.now().strftime("%Y-%m-%d")