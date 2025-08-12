from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from a .env file if it exists

import os, asyncio
from ._foundry_agent import FoundryAgent

class SkFoundryAgent:
    """Singleton wrapper exposed to FastAPI."""

    def __init__(self) -> None:
        self._agent = None

    async def ask(self, query: str) -> str:
        # Initialize once the agent
        if self._agent is None:       
            self._agent = await FoundryAgent.create()
        
        # Set the prompt
        prompt = query
                
        # Interact with _foundry_agent as needed
        # It's for direct console type client calls. The async context manager guarantees the aiohttp session and connector are closed before the event loop shuts down, eliminating the runtime warnings and allowing response to be printed normally.
        # For fastapi way of call for run api, lifecycle session wrapper is not to be used.
        # async with self._agent.lifecycle():
            # results = await self._agent.run(prompt)
        results = await self._agent.run(prompt)
        
        return results