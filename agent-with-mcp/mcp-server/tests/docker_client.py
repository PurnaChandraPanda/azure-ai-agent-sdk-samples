"""
Run from the repository root:
    uv run examples/snippets/clients/streamable_basic.py
"""

import asyncio
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

# import logging
# import sys
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

async def main():
    # Connect to a streamable HTTP server
    async with streamable_http_client("http://localhost:40027/mcp") as (
        read_stream,
        write_stream,
        _,
    ):
        # Create a session using the client streams
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")

            # Find the "add" tool
            add_tool = next((t for t in tools.tools if t.name == "add"), None)
            if not add_tool:
                raise RuntimeError("Tool 'add' not found")

            print("Add tool input schema:", json.dumps(add_tool.inputSchema, indent=2))

            # Call the tool with typical args (adjust keys based on schema)
            # Common schemas use {"a": <number>, "b": <number>}
            result = await session.call_tool("add", {"a": 2, "b": 3})

            # Handle result content blocks
            if getattr(result, "isError", False):
                print("Tool returned an error")
            for block in getattr(result, "content", []):
                # Blocks are usually text or json
                if getattr(block, "type", None) == "text":
                    print("Result (text):", block.text)
                elif getattr(block, "type", None) == "json":
                    # Some SDKs use .value, some use .json — try both defensively
                    value = getattr(block, "value", None) or getattr(block, "json", None)
                    print("Result (json):", json.dumps(value, indent=2))
                else:
                    print("Result (other):", block)



if __name__ == "__main__":
    asyncio.run(main())