from langchain.tools import BaseTool
from ._foundry_agent import FoundryAgent

class FoundryAgentTool(BaseTool):
    name: str = "azure_foundry_agent"
    description: str = (
        "Send a user query to the Azure AI Foundry Agents service "
        "and return the assistant's answer."
    )

    def __init__(self, **data):
        super().__init__(**data)
        self._bing_agent = FoundryAgent()

    # BaseTool contract
    def _run(self, query: str, run_manager=None, **kwargs) -> str:
        return self._bing_agent.answer_query(query)

    async def _arun(self, query: str, run_manager=None, **kwargs) -> str:
        raise NotImplementedError()