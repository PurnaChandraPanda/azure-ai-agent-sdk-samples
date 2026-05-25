# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run Prompt Agent operations
    using MCP (Model Context Protocol) tools and an asynchronous client.

USAGE:
    python sample_agent_mcp_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
import asyncio
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool, Tool


load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]


async def main():
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):
        mcp_tool = MCPTool(
            server_label=os.environ["MCP_SERVER_LABEL"],
            server_url=os.environ["MCP_SERVER_URL"],
            require_approval="never",
        )

        # Create tools list with proper typing for the agent definition
        tools: list[Tool] = [mcp_tool]

        # Create a prompt agent with MCP tool capabilities
        agent = await project_client.agents.create_version(
            agent_name=os.environ["V2_AGENT_NAME"],
            definition=PromptAgentDefinition(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                instructions="You are a helpful agent that can use MCP tools to assist users. Use the available MCP tools to answer questions and perform tasks.",
                tools=tools,
            ),
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")


if __name__ == "__main__":
    asyncio.run(main())