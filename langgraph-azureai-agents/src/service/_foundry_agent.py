from __future__ import annotations
import os
from functools import lru_cache
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

@lru_cache(maxsize=1)
def _get_project_client(endpoint: str) -> AIProjectClient:
    """Return a cached AIProjectClient (created only once per process)."""

    ## If env var is set for AZURE_CONTAINERAPP_CLIENT_ID, use it as default credential.
    ## This will cover for Azure Contaner Apps cases.
    ## If not set, it will use empty constructor for DefaultAzureCredential - in local machine.
    if "AZURE_CONTAINERAPP_CLIENT_ID" in os.environ:
        msi_client_id = os.environ["AZURE_CONTAINERAPP_CLIENT_ID"]
        cred = DefaultAzureCredential(managed_identity_client_id=msi_client_id)
    else:
        cred = DefaultAzureCredential()

    return AIProjectClient(
        endpoint=endpoint,
        credential=cred,
    )

class FoundryAgent:
    """A class to interact with the Azure AI Foundry Agents service using a synchronous client.
    This class provides a method to send queries to a Foundry agent and retrieve responses.
    """

    def __init__(self) -> None:
        """Initialize the FoundryBingAgent with environment variables."""
        # Ensure required environment variables are set
        if "PROJECT_ENDPOINT" not in os.environ or "AZURE_FOUNDRY_AGENT_ID" not in os.environ:
            raise EnvironmentError("Required environment variables are not set.")

        self._endpoint = os.environ["PROJECT_ENDPOINT"]
        self._agent_id = os.environ["AZURE_FOUNDRY_AGENT_ID"]

        ## Reuse the cached project client
        self._project_client = _get_project_client(self._endpoint)    
    

    def answer_query(self, query: str) -> str:
        """Send *query* to the Foundry agent and return its response text."""
        thread = self._project_client.agents.threads.create()
        try:
            # Create a message in the thread with the user's query
            self._project_client.agents.messages.create(
                thread_id=thread.id, 
                role="user", 
                content=query)
            # Create and process the agent run
            run = self._project_client.agents.runs.create_and_process(
                thread_id=thread.id, 
                agent_id=self._agent_id)
            if run.status == "failed":
                raise RuntimeError(f"Agent run failed: {run.last_error}")
        
            ## Retrieve the assistant's response from the thread messages
            msgs = list(self._project_client.agents.messages.list(thread_id=thread.id))
            assistant_message = next(
                (m for m in reversed(msgs) if m.role == "assistant"), 
                None)
            
            if assistant_message is None:
                raise RuntimeError("Agent run completed, but no assistant response found in the thread messages.")
            
            # Return the content of the assistant's message
            return assistant_message.content
        finally:
            ## Clean up the thread after processing
            self._project_client.agents.threads.delete(thread_id=thread.id)