# Copyright (c) Microsoft. All rights reserved.

import asyncio
from typing import Any
import os

from agent_framework import AgentProtocol, AgentResponse, AgentThread, ChatMessage, HostedMCPTool
from agent_framework.azure import AzureAIProjectAgentProvider
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv

load_dotenv()

"""
Azure AI Agent with Hosted MCP Example

This sample demonstrates integrating hosted Model Context Protocol (MCP) tools with Azure AI Agent.
"""


async def create_hosted_mcp_without_approval() -> None:
    """Example showing MCP Tools without approval."""
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        AzureAIProjectAgentProvider(credential=credential) as provider,
    ):
        agent = await provider.create_agent(
            name=os.environ["AZURE_AI_AGENT1_AGENT_NAME"],
            instructions="You are a helpful agent that can use MCP tools to assist users.",
            tools=HostedMCPTool(
                name=os.environ["MCP_SERVER_LABEL"],
                url=os.environ["MCP_SERVER_URL"],
                approval_mode="never_require",
            ),
        )

        print(f"Agent '{agent.name}' created with Hosted MCP Tool requiring no approval.")


async def create_hosted_mcp_with_approval_and_thread() -> None:
    """Example showing MCP Tools with approvals using a thread."""
    print("=== MCP with approvals and with thread ===")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        AzureAIProjectAgentProvider(credential=credential) as provider,
    ):
        agent = await provider.create_agent(
            name=os.environ["AZURE_AI_AGENT2_AGENT_NAME"],
            instructions="You are a helpful agent that can use MCP tools to assist users.",
            tools=HostedMCPTool(
                name=os.environ["MCP_SERVER_LABEL"],
                url=os.environ["MCP_SERVER_URL"],
                approval_mode="always_require",
            ),
        )

        print(f"Agent '{agent.name}' created with Hosted MCP Tool requiring approval.")


async def main() -> None:
    print("=== Azure AI Agent with Hosted MCP Tools Example ===\n")

    await create_hosted_mcp_without_approval()
    await create_hosted_mcp_with_approval_and_thread()


if __name__ == "__main__":
    asyncio.run(main())