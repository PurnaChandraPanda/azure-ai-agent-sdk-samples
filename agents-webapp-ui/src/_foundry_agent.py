from ast import List
import os
import asyncio
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentThread
from semantic_kernel.contents import ChatMessageContent, FunctionCallContent, FunctionResultContent
from contextlib import asynccontextmanager, suppress

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

class FoundryAgent:
    def __init__(self, agent_definition, agent, *, client, credential):
        self.agent_definition = agent_definition
        self.agent = agent
        self._client = client
        self._credential = credential

    @classmethod
    async def create(cls):
        ## If env var is set for AZURE_CONTAINERAPP_CLIENT_ID, use it as default credential.
        ## This will cover for Azure Contaner Apps cases.
        ## If not set, it will use empty constructor for DefaultAzureCredential - in local machine.
        if "AZURE_CONTAINERAPP_CLIENT_ID" in os.environ:
            msi_client_id = os.environ["AZURE_CONTAINERAPP_CLIENT_ID"]
            _credentials = DefaultAzureCredential(managed_identity_client_id=msi_client_id)
        else:
            _credentials = DefaultAzureCredential()
        _project_client = AzureAIAgent.create_client(
                            credential=_credentials,                            
                            endpoint = os.environ["AZURE_AI_AGENT_ENDPOINT"],  # Ensure this environment variable is set
                        )
        
        # Retrieve the agent definition based on the `agent_id`
        _agent_definition = await _project_client.agents.get_agent(
            agent_id=os.environ["AZURE_AI_AGENT_AGENT_ID"]  # Ensure this environment variable is set            
        )

        _agent = AzureAIAgent(
            client=_project_client,  # Ensure `client` is defined or fetched as needed
            definition=_agent_definition,
        )

        return cls(_agent_definition, _agent, client=_project_client, credential=_credentials)

    async def handle_streaming_intermediate_steps(self, message: ChatMessageContent) -> None:
        for item in message.items or []:
            if isinstance(item, FunctionResultContent):
                print(f"Function Result:> {item.result} for function: {item.name}")
            elif isinstance(item, FunctionCallContent):
                print(f"Function Call:> {item.name} with arguments: {item.arguments}")
            else:
                print(f"{item}")

    async def run(self, user_prompt):
        """
        Run the agent with the provided prompt and return the response.
        """
        if not self.agent:
            raise ValueError("Agent is not initialized.")

        try:
            # Create a thread for the agent to run in
            thread: AzureAIAgentThread = None
            chunks: List[str] = []
            
            # Invoke the agent for the specified thread for response
            async for response in self.agent.invoke_stream(
                    messages=user_prompt,
                    thread=thread,
                    on_intermediate_message=self.handle_streaming_intermediate_steps,
                ):
                response_text = getattr(response, "content", None)
                chunks.append(str(response_text) if response_text is not None else str(response))   # accumulate
                
                # Print the agent's response
                print(f"{response}", end="", flush=True)
                # Update the thread for subsequent messages
                thread = response.thread

        finally:
            # Clean up the thread if it was created
            if thread:
                await thread.delete()        

        return "".join(chunks) if chunks else "No response received."

    @asynccontextmanager
    async def lifecycle(self):
        """
        Handle the lifecycle of the agent, including cleanup.
        """
        try:
            yield self
        finally:
            # flush any pending network ops
            # lets any in-flight callbacks finish before the session is torn down
            await asyncio.sleep(0)
            # close client (closes its aiohttp session)
            if hasattr(self._client, "close"):
                await self._client.close()
            # close credential transport
            with suppress(Exception):
                if hasattr(self._credential, "close"):
                    await self._credential.close()