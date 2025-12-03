"""Searxng via MCP for LLMs."""

import tomllib
from pathlib import Path
from typing import Any

from httpx import AsyncClient, Response
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


class SearchResponse(BaseModel):
    """Response model."""

    query: str
    number_of_results: int
    results: list[SearchResult]
    infoboxes: list[Infobox]


async def search_searxng(query: str, limit: int = 10) -> str:
    """Search searxng."""
    searxng_url = "http://localhost:8888"

    config_path: Path = Path().home() / ".mcp.toml"
    if config_path.exists():
        with open(file=config_path, encoding="utf-8") as f:
            config: dict[str, Any] = tomllib.load(f=f)
            if "searxng" in config:
                searxng_url: str = config["searxng"]["url"]
    client = AsyncClient(base_url=searxng_url)

    params: dict[str, str] = {"q": query, "format": "json"}

    response: Response = await client.get(url="/search", params=params)
    response.raise_for_status()

    data: SearchResponse = SearchResponse.model_validate_json(json_data=response.text)

    text: str = ""

    for _index, infobox in enumerate(iterable=data.infoboxes):
        text += f"Infobox: {infobox.infobox}\n"
        text += f"ID: {infobox.id}\n"
        text += f"Content: {infobox.content}\n"
        text += "\n"

    if len(data.results) == 0:
        text += "No results found\n"

    for index, result in enumerate(iterable=data.results):
        text += f"Title: {result.title}\n"
        text += f"URL: {result.url}\n"
        text += f"Content: {result.content}\n"
        text += "\n"

        if index == limit - 1:
            break

    return str(text)


# Create a named server
mcp = FastMCP(name="Searxng via MCP")


@mcp.tool()
async def search_tool(message: str) -> str:
    """Search online for information via Searxng."""
    result: str = await search_searxng(query=message)
    return result
