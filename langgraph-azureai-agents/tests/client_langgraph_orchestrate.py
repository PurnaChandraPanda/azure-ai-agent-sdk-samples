import asyncio
from src.service.langgraph_agent_service import LanggraphFoundryAgent


if __name__ == "__main__":
    _service = LanggraphFoundryAgent()
    query = "5 supply chain news for microsoft"
    result = asyncio.run(_service.ask(query))
    # print(f"Result: {result['output']}\n")
    print(f"Result: {result}\n")

