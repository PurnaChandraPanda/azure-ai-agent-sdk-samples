from __future__ import annotations

import asyncio
import json
import os

from azure.identity import DefaultAzureCredential
from typing import Any

from dotenv import load_dotenv

from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.foundry import FoundryChatClient

load_dotenv(override=True)


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

def print_mcp_result(result: Any) -> None:
    content_items = getattr(result, "content", None)

    if not content_items:
        print(result)
        return

    for item in content_items:
        item_type = getattr(item, "type", None)
        item_text = getattr(item, "text", None)

        if item_type == "text" and item_text:
            try:
                parsed = json.loads(item_text)
                print(json.dumps(parsed, indent=2))
            except json.JSONDecodeError:
                print(item_text)
        else:
            print(item)


async def main() -> None:
    mcp_server_url = get_required_env("MCP_SERVER_URL")

    # will automatically read env values and pass to chat client
    client=FoundryChatClient(credential=DefaultAzureCredential())

    async with (
        MCPStreamableHTTPTool(
            name="tee-time-mcp-server",
            url=mcp_server_url,
            description=(
                "MCP server exposing player_query and teetime_action tools "
                "for player lookup, tee time search, and tee time booking."
            ),
            request_timeout=60,
        ) as mcp_server,
        Agent(
            client=client,
            name="tee-time-agent",
            instructions=(
                "You are a tee time booking assistant. "
                "Use the MCP tools to search players, search tee times, and book tee times. "
                "Use player_query when an existing player needs lookup. "
                "Use teetime_action for tee time search and booking. "
                "If a tool returns an error payload with guidance, summarize the guidance clearly."
            ),
        ) as agent,
    ):
        print("\n✔️✔️ ### Agent invocation using MCP tools ###")

        user_prompt = (
            "Search tee times for property PROP-001 using local search. "
            "Tell me the available teeTimeId values."
        )
        
        result = await agent.run(
            user_prompt,
            tools=mcp_server,
        )

        print("✅✅ ", result)

        print("\n✔️✔️ ### Agent invocation using MCP tools - handled error ###")

        user_prompt = (
            "Search tee times for property PROP-001 using platform search. "
            "If the tool returns an error, explain the errorCode and guidance."
        )
        
        result = await agent.run(
            user_prompt,
            tools=mcp_server,
        )

        print("✅✅ ", result)


if __name__ == "__main__":
    asyncio.run(main())


