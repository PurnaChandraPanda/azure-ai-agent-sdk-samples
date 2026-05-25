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
from openai.types.responses.response_input_param import McpApprovalResponse, ResponseInputParam

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]


def _collect_mcp_approval_responses(response, expected_server_label: str) -> list[dict]:
    """
    Scan response.output for MCP approval requests and build approval response items.
    Returns a list of input items suitable to send as the next responses.create(input=...).
    """
    approvals: list[dict] = []
    for item in getattr(response, "output", []) or []:
        if getattr(item, "type", None) == "mcp_approval_request":
            # Only approve the MCP server you expect (defense-in-depth)
            if getattr(item, "server_label", None) == expected_server_label and getattr(item, "id", None):
                approvals.append(
                    {
                        "type": "mcp_approval_response",
                        "approve": True,
                        "approval_request_id": item.id,
                    }
                )
    return approvals


async def main(_input: str):
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        # Read agent created in the previous step
        agent_name = os.environ["V2_AGENT_NAME"]

        # Create a conversation thread to maintain context across multiple interactions
        conversation = await openai_client.conversations.create()
        print(f"Created conversation (id: {conversation.id})")

        # Send initial request that will trigger the MCP tool
        response = await openai_client.responses.create(
            conversation=conversation.id,
            input=_input,
            extra_body={"agent": {"name": agent_name, "type": "agent_reference"}},
        )

        expected_server_label = os.environ["MCP_SERVER_LABEL"]

        # Process any MCP approval requests that were generated
        approvals = _collect_mcp_approval_responses(response, expected_server_label)

        if approvals:
            print(f"Approving {len(approvals)} MCP request(s) for '{expected_server_label}' ...")

            response = await openai_client.responses.create(
                                previous_response_id=response.id,
                                input=approvals,
                                extra_body={"agent": {"name": agent_name, "type": "agent_reference"}},
                            )

        
        # No approvals pending => we can treat this as progressed/final.
        # output_text is the easiest way to read the assistant's final text response.
        text = getattr(response, "output_text", None)
        if text:
            print("Agent response:")
            print(text)
            return


if __name__ == "__main__":
    # _input = "add 15 and 12"
    # _input = "subtract 15 from 12"
    # _input = "multiply 2 and 5"
    _input = "divide 10 by 4.5"
    asyncio.run(main(_input))