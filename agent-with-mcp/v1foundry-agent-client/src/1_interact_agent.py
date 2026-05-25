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

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

PROJECT_ENDPOINT = os.environ["AZURE_EXISTING_AIPROJECT_ENDPOINT"]

def main(user_input: str):
    # Create the AI Project Client
    project_client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential()
    )

    # Retrieve the agent definition based on the `agent_id`
    agent = project_client.agents.get_agent(
                        agent_id=os.environ["AZURE_AI_AGENT_AGENT_ID"]  # Ensure this environment variable is set            
                        )
    print(f"Retrieved agent, agent ID: {agent.id}")

    # Create a thread for the agent to run in
    thread = project_client.agents.threads.create()
    print(f"Created thread, thread ID: {thread.id}")

    # Create a message from the user to start the interaction
    message = project_client.agents.messages.create(
        thread_id=thread.id, role="user", content=user_input,
        )
    print(f"Created message, message ID: {message.id}")

    mcp_server_label = os.environ["MCP_SERVER_LABEL"]
    mcp_server_url = os.environ["MCP_SERVER_URL"]

    # Initialize agent MCP tool
    mcp_tool = McpTool(
        server_label=mcp_server_label,
        server_url=mcp_server_url,
    )

    # Set the approved tools for the MCP tool: never
    mcp_tool.set_approval_mode("never")

    # Create a run for the agent with the created thread
    run = project_client.agents.runs.create(
            thread_id=thread.id, 
            agent_id=agent.id,
            tool_resources=mcp_tool.resources)

    # Poll the run as long as run status is queued or in progress
    while run.status in ["queued", "in_progress", "requires_action"]:
        # Wait for a second
        time.sleep(1)
        run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
        print(f"Run status: {run.status}")

        # Poll and handle requires_action (tool approval is client-side)
        if run.status == "requires_action" and isinstance(run.required_action, SubmitToolApprovalAction):
            approvals = []
            for tc in run.required_action.submit_tool_approval.tool_calls:
                if isinstance(tc, RequiredMcpToolCall):
                    approvals.append(
                        ToolApproval(
                            tool_call_id=tc.id,
                            approve=True,
                            headers=mcp_tool.headers,
                        )
                    )

            if approvals:
                run = project_client.agents.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    approvals=approvals,
                )
    
    # if run failed, print the error
    if run.status == "failed":
        print(f"Run error: {run.last_error}")

    # Fetch and print run steps and messages
    run_steps = project_client.agents.run_steps.list(thread_id=thread.id, run_id=run.id)
    for step in run_steps:
        print(f"Run step: {step.id}, status: {step.status}, type: {step.type}")
        if step.type == "tool_calls":
            print(f"Tool call details:")
            for tool_call in step.step_details.tool_calls:
                print(json.dumps(tool_call.as_dict(), indent=2))

    # Fetch and print all messages in the thread
    messages = project_client.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for data_point in messages:
        last_message_content = data_point.content[-1]
        if isinstance(last_message_content, MessageTextContent):
            print(f"{data_point.role}: {last_message_content.text.value}")


if __name__ == "__main__":
    # _input = "add 15 and 33"
    _input = "greet the msft team"
    main(_input)