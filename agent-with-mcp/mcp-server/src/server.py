
# server.py
import uvicorn
from fastapi import FastAPI
import threading
import sys
import time

from mcp.server.fastmcp import FastMCP

from ._logging_config import configure_logger

# Configure the logger
_logger = configure_logger(__name__)


# 1) Start a tiny FastAPI health server in the same process (different port)
def start_health_api(host=None, port=None):
    # Default host and port
    host = host or "127.0.0.1"
    port = port or 8001

    # Create FastAPI app for health checks
    app = FastAPI(title="Health API", docs_url=None, redoc_url=None)

    @app.get("/healthz")
    async def healthz():
        return {
            "status": "ok",
            "service": "mcp",
        }

    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)
    t = threading.Thread(target=server.run, name="health-api", daemon=True)
    t.start()
    _logger.info("Health API started on http://%s:%s/healthz", host, port)
    return t


# 2) Create the MCP server (name will be visible to clients)
## By default the host is set to 127.0.0.1 which doesn't allow external connections outside of the local machine to connect. 
## So, when hosting it in Azure or docker-compose or other server, nothing from outside the machine is allowed to connect. 
## Setting it to 0.0.0.0 tells the program to listen on all interfaces and accept connections from all networks.
mcp = FastMCP(
        "My Tools Server", 
        json_response=True,
        host="0.0.0.0", # 
        port=8000, # explicitly set port here as well, though default is 8000
)

# --- Tools ---
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    _logger.info(f"add(): {a} and {b}")

    ## logic
    result = a + b
    
    _logger.info(f"add() result: {result}")
    return result

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    _logger.info(f"subtract(): {a} minus {b}")

    ## logic
    time.sleep(50)  # Simulate a longer operation
    result = a - b
    
    _logger.info(f"subtract() result: {result}")
    return result

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    _logger.info(f"multiply(): {a} times {b}")

    ## logic
    time.sleep(45*2)  # Simulate a longer operation
    result = a * b
    
    _logger.info(f"multiply() result: {result}")
    return result

@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide two numbers"""
    _logger.info(f"divide(): {a} divided by {b}")

    if b == 0:
        _logger.error("divide() error: Division by zero")
        raise ValueError("Cannot divide by zero")

    ## logic
    time.sleep(40*2.5)  # Simulate a longer operation
    result = a / b
    
    _logger.info(f"divide() result: {result}")
    return result

# --- Resources ---
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Personalized greeting resource"""
    return f"Hello, {name}!"

# --- Prompts ---
@mcp.tool()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    return f"Write a {style} greeting for someone named {name}."


def main():
    ## Local variables
    host = port = None

    ## Check if the script is run with command line arguments
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    # Start health API in separate thread
    start_health_api(host, port)
    
    # Start Streamable HTTP transport (GET for streaming, POST for messages)
    # Default port is 8000; you can override with env vars
    # Set the default host to 0.0.0.0 to listen on all interfaces
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    main()
