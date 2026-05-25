# Copyright (c) Microsoft. All rights reserved.

import asyncio
from typing import Any
import os

from agent_framework import AgentProtocol, AgentResponse, AgentThread, HostedMCPTool
from agent_framework.azure import AzureAIAgentsProvider
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv, set_key
from pathlib import Path

load_dotenv()

"""
Azure AI Agent with Hosted MCP Example

This sample demonstrates integration of Azure AI Agents with hosted Model Context Protocol (MCP)
servers, including user approval workflows for function call security.
"""

def _save_agent_id_to_env(agent_id: str):
    src_dir = Path(__file__).resolve().parent
    env_path = src_dir / '.env'
    if not env_path.exists():
        env_path.touch()
    set_key(env_path, "AZURE_AI_AGENT_AGENT_ID", agent_id, quote_mode="never")

    return env_path

async def handle_approvals_with_thread(query: str, agent: "AgentProtocol", thread: "AgentThread") -> AgentResponse:
    """Here we let the thread deal with the previous responses, and we just rerun with the approval."""
    from agent_framework import ChatMessage

    result = await agent.run(query, thread=thread, store=True)
    while len(result.user_input_requests) > 0:
        new_input: list[Any] = []
        for user_input_needed in result.user_input_requests:
            print(
                f"User Input Request for function from {agent.name}: {user_input_needed.function_call.name}"
                f" with arguments: {user_input_needed.function_call.arguments}"
            )
            user_approval = input("Approve function call? (y/n): ")
            new_input.append(
                ChatMessage(
                    role="user",
                    contents=[user_input_needed.create_response(user_approval.lower() == "y")],
                )
            )
        result = await agent.run(new_input, thread=thread, store=True)
    return result


async def main() -> None:
    """Example showing Hosted MCP tools for a Azure AI Agent."""
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentsProvider(credential=credential) as provider,
    ):
        agent = await provider.create_agent(
            name="MCP Helper Agent",
            instructions="You are a helpful assistant.",
            tools=HostedMCPTool(
                name=os.environ["MCP_SERVER_LABEL"],
                url=os.environ["MCP_SERVER_URL"],
            ),
        )

        print(f"Created agent: {agent.name}, id: {agent.id}")

        # Save the agent ID to .env file for later use
        ## Find the line that starts with AZURE_AI_AGENT_AGENT_ID and replace it, or add it if not present
        env_path = _save_agent_id_to_env(agent.id)    
        
        print("Agent ID saved to .env file at: ", env_path)


if __name__ == "__main__":
    asyncio.run(main())