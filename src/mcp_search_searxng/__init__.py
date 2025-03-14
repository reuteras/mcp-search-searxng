"""Init file."""

import sys

from mcp_search_searxng.server import search_searxng


def main() -> None:
    """Function not used."""
    import asyncio

    print(asyncio.run(main=search_searxng(query=sys.argv[1])))
