from src._foundry_agent import FoundryAgent
import asyncio

async def main(prompt):
    # Call the async founder agent API
    _foundry_agent = await FoundryAgent.create()

    # The async context manager guarantees the aiohttp session and connector are closed before the event loop shuts down, eliminating the runtime warnings and allowing response to be printed normally.
    # Interact with _foundry_agent as needed
    async with _foundry_agent.lifecycle():
        return await _foundry_agent.run(prompt)

if __name__ == "__main__":
    prompt = "top 5 supply chain news on MSFT"  # Replace with your actual prompt
    # Run the main function to process the prompt
    response = asyncio.run(main(prompt))
    print("\n----\n", response)