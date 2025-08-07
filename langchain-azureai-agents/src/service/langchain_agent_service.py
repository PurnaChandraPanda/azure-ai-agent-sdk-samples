from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from a .env file if it exists

import os, asyncio
from functools import lru_cache
from azure.identity import DefaultAzureCredential
from langchain.agents import initialize_agent
from langchain_openai import AzureChatOpenAI
from ._foundry_agent_tool import FoundryAgentTool


@lru_cache(maxsize=1)
def _build_agent():
    ## If env var is set for AZURE_CONTAINERAPP_CLIENT_ID, use it as default credential.
    ## This will cover for Azure Contaner Apps cases.
    ## If not set, it will use empty constructor for DefaultAzureCredential - in local machine.
    if "AZURE_CONTAINERAPP_CLIENT_ID" in os.environ:
        msi_client_id = os.environ["AZURE_CONTAINERAPP_CLIENT_ID"]
        cred = DefaultAzureCredential(managed_identity_client_id=msi_client_id)
    else:
        cred = DefaultAzureCredential()

    def _aad_token_provider() -> str:
        return cred.get_token("https://cognitiveservices.azure.com/.default").token

    llm = AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment_name=os.environ["MODEL_DEPLOYMENT_NAME"],
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-04-01-preview"),
        azure_ad_token_provider=_aad_token_provider,
    )

    return initialize_agent(
        tools=[FoundryAgentTool()],
        llm=llm,
        agent="openai-functions",
        verbose=False,
        handle_parsing_errors=True,
    )


class LangchainFoundryAgent:
    """Singleton wrapper exposed to FastAPI."""

    def __init__(self) -> None:
        self._agent = _build_agent()

    async def ask(self, query: str) -> str:
        # run blocking invoke in a worker thread
        return await asyncio.to_thread(self._agent.invoke, query)