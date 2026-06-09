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

    pip install "azure-ai-projects>=2.0.0" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
import asyncio
from dotenv import load_dotenv
from typing import Any
from openai.types.responses.response_input_param import McpApprovalResponse, ResponseInputParam
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool, Tool

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]

def extract_response_text(response: Any) -> str:
    """
    Extract assistant output text from OpenAI Responses API response object.
    Handles response.output[].content[].text shape.
    """
    texts: list[str] = []

    for output_item in getattr(response, "output", []) or []:
        if getattr(output_item, "type", None) != "message":
            continue

        for content_item in getattr(output_item, "content", []) or []:
            text = getattr(content_item, "text", None)
            if text:
                texts.append(text)

    return "\n".join(texts)


def print_response_summary(response: Any) -> None:
    usage = getattr(response, "usage", None)

    input_tokens = getattr(usage, "input_tokens", None) if usage else None
    output_tokens = getattr(usage, "output_tokens", None) if usage else None
    total_tokens = getattr(usage, "total_tokens", None) if usage else None

    input_details = getattr(usage, "input_tokens_details", None) if usage else None
    output_details = getattr(usage, "output_tokens_details", None) if usage else None

    cached_tokens = (
        getattr(input_details, "cached_tokens", None)
        if input_details
        else None
    )

    reasoning_tokens = (
        getattr(output_details, "reasoning_tokens", None)
        if output_details
        else None
    )

    output_text = extract_response_text(response)

    print("\n➕➕ ### Agent Response Summary ###")
    print(f"Response ID      : {getattr(response, 'id', None)}")
    print(f"Status           : {getattr(response, 'status', None)}")
    print(f"Model            : {getattr(response, 'model', None)}")
    print(f"Error            : {getattr(response, 'error', None)}")

    print("\n### Response Output Text ###")
    print(output_text if output_text else "<no output text found>")

    print("\n### Token Usage ###")
    print(f"Input tokens     : {input_tokens}")
    print(f"Output tokens    : {output_tokens}")
    print(f"Cached tokens    : {cached_tokens}")
    print(f"Reasoning tokens : {reasoning_tokens}")
    print(f"Total tokens     : {total_tokens}")

async def main():
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        # Read agent created in the previous step
        agent_name = os.environ["FOUNDRY_AGENT_NAME"]

        # Create a conversation thread to maintain context across multiple interactions
        conversation = await openai_client.conversations.create()
        print(f"Created conversation (id: {conversation.id})")

        # Specify the input prompt
        # input_message=(
        #     "Search tee times for property PROP-001 using local search. "
        #     "Tell me the available teeTimeId values."
        # )

        input_message=(
            "Search tee times for property PROP-001 using platform search. "
            "If the tool returns an error, explain the errorCode and guidance."
        )

        # Send initial request that will trigger the MCP tool
        response = await openai_client.responses.create(
            conversation=conversation.id,
            input=input_message,
            extra_body={"agent_reference": {"name": agent_name, "type": "agent_reference"}},
        )

        # Process any MCP approval requests that were generated
        input_list: ResponseInputParam = []
        for item in response.output:
            if item.type == "mcp_approval_request":
                if item.server_label == os.environ["MCP_SERVER_LABEL"] and item.id:
                    # Automatically approve the MCP request to allow the agent to proceed
                    # In production, you might want to implement more sophisticated approval logic
                    input_list.append(
                        McpApprovalResponse(
                            type="mcp_approval_response",
                            approve=True,
                            approval_request_id=item.id,
                        )
                    )

        print("Final input:")
        print(input_list)

        # Send the approval response back to continue the agent's work
        # This allows the MCP tool to access the GitHub repository and complete the original request
        response = await openai_client.responses.create(
            input=input_list,
            previous_response_id=response.id,
            extra_body={"agent_reference": {"name": agent_name, "type": "agent_reference"}},
        )

        # print(f"Agent response: {response}")
        # print(f"Agent response: {response.output_text}")
        print_response_summary(response)

        


if __name__ == "__main__":
    asyncio.run(main())