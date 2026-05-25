import time
import json

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import MessageTextContent, ListSortOrder
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    ListSortOrder,
    McpTool,
    RequiredMcpToolCall,
    RunStepActivityDetails,
    SubmitToolApprovalAction,
    ToolApproval,
)

from dotenv import load_dotenv, set_key
import os
from pathlib import Path

# Load environment variables
load_dotenv()

PROJECT_ENDPOINT = os.getenv("AZURE_EXISTING_AIPROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME")


def _save_agent_id_to_env(agent_id: str):
    src_dir = Path(__file__).resolve().parent
    env_path = src_dir / '.env'
    if not env_path.exists():
        env_path.touch()
    set_key(env_path, "AZURE_AI_AGENT_AGENT_ID", agent_id, quote_mode="never")

    return env_path


def main():
    # Create the AI Project Client
    project_client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential()
    )

    mcp_server_label = os.environ["MCP_SERVER_LABEL"]
    mcp_server_url = os.environ["MCP_SERVER_URL"]

    # Initialize agent MCP tool
    mcp_tool = McpTool(
        server_label=mcp_server_label,
        server_url=mcp_server_url,
    )

    # Set the approved tools for the MCP tool: never
    mcp_tool.set_approval_mode("never")

    with project_client:
        agent = project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT_NAME, 
            name="my-classic-mcp-agent", 
            instructions="You are a helpful assistant. Use the tools provided to answer the user's questions. Be sure to cite your sources.",
            tools=mcp_tool.definitions,
        )
        print(f"Created agent, agent ID: {agent.id}")

        # Save the agent ID to .env file for later use
        ## Find the line that starts with AZURE_AI_AGENT_AGENT_ID and replace it, or add it if not present
        env_path = _save_agent_id_to_env(agent.id)    
        
        print("Agent ID saved to .env file at: ", env_path)


if __name__ == "__main__":
    main()