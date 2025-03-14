"""Searxng via MCP for LLMs."""

from httpx import AsyncClient
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel


class SearchResult(BaseModel):
    """SearchResult model."""

    url: str
    title: str
    content: str


class InfoboxUrl(BaseModel):
    """InfoboxUrl model."""

    title: str
    url: str


class Infobox(BaseModel):
    """Infobox model."""

    infobox: str
    id: str
    content: str
    urls: list[InfoboxUrl]


class Response(BaseModel):
    """Response model."""

    query: str
    number_of_results: int
    results: list[SearchResult]
    infoboxes: list[Infobox]


async def search_searxng(query: str, limit: int = 10) -> str:
    """Search searxng."""
    client = AsyncClient(base_url="https://hetzner.tail9e5e41.ts.net:8443/searxng")

    params: dict[str, str] = {"q": query, "format": "json"}

    response = await client.get("/search", params=params)
    response.raise_for_status()

    data = Response.model_validate_json(response.text)

    text: str = ""

    for _index, infobox in enumerate(data.infoboxes):
        text += f"Infobox: {infobox.infobox}\n"
        text += f"ID: {infobox.id}\n"
        text += f"Content: {infobox.content}\n"
        text += "\n"

    if len(data.results) == 0:
        text += "No results found\n"

    for index, result in enumerate(data.results):
        text += f"Title: {result.title}\n"
        text += f"URL: {result.url}\n"
        text += f"Content: {result.content}\n"
        text += "\n"

        if index == limit - 1:
            break

    return str(text)


# Create a named server
mcp = FastMCP("Searxng via MCP")


@mcp.tool()
async def search_tool(message: str) -> str:
    """Search online for information via Searxng."""
    result = await search_searxng(message)
    return result
