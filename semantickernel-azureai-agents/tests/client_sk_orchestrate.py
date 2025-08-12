import asyncio
from src.service.sk_agent_service import SkFoundryAgent


if __name__ == "__main__":
    _service = SkFoundryAgent()
    query = "5 supply chain news for microsoft"
    result = asyncio.run(_service.ask(query))
    # print(f"Result: {result['output']}\n")
    print(f"Result: {result}\n")

