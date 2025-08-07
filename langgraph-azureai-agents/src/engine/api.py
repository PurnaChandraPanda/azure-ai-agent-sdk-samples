import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import uvicorn
from ..service.langgraph_agent_service import LanggraphFoundryAgent
from ._logging_config import configure_logger

_logger = configure_logger(__name__)

_agent_service: LanggraphFoundryAgent | None = None

@asynccontextmanager
async def _startup(app: FastAPI):
    global _agent_service
    _agent_service = LanggraphFoundryAgent()

    try:
        yield  # FastAPI runs the app while suspended here
    finally:
        # Cleanup if needed
        _agent_service = None

## intialize fastapi app
app = FastAPI(lifespan=_startup, title="Foundry Agent Gateway")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    query: str


class Answer(BaseModel):
    answer: str


@app.post("/ask", response_model=Answer)
async def ask_endpoint(data: Query) -> Answer:
    _logger.info("Received query")

    try:
        result = await _agent_service.ask(data.query)
        return Answer(answer=result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        _logger.info("Query processing completed")

@app.get("/health")
def health():
    """Check if server is healthy. Used by the readiness probe to check server is healthy."""
    return "healthy"


def main():
    host = ""
    port = ""

    ## Check if the script is run with command line arguments
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    ## Run the uvicorn server for fastapi app
    uvicorn.run(
        "__main__:app", 
        host=host, 
        port=port
    )

if __name__ == '__main__':
    main()