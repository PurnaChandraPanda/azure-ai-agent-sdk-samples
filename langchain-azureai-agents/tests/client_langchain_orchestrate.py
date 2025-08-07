import asyncio
from src.service.langchain_agent_service import LangchainFoundryAgent


if __name__ == "__main__":
    _service = LangchainFoundryAgent()
    query = "5 supply chain news for reliance"
    result = asyncio.run(_service.ask(query))
    print(f"Result: {result['output']}\n")

