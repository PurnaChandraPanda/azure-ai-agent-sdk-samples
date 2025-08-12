# Architecture Overview: Semantic Kernel Azure AI Agents

## 1. Introduction
This document describes the architecture of the `semantickernel-azureai-agents` component, which provides a FastAPI-based gateway to Azure AI Agents using the Semantic Kernel SDK.

## 2. High-Level Diagram
- Client ---HTTP----> POST /ask | FastAPI (engine/api)
- FastAPI ----Sevice Layer---> semantic-kernel AzureAIAgent APIs
- AzureAIAgent ----> Azure AI Agent service (already created on Azure Foundry)

## 3. Folder Structure
semantickernel-azureai-agents/
├── src
    ├── engine/ # HTTP gateway
    │   ├── _logging_config.py
    │   └── api.py
    └── service/ # Service layer - Agent management
        ├── _foundry_agent.py
        └── sk_agent_service.py

## 4. Components

### 4.1 Engine (API Layer)
- **api.py**  
  - Defines a FastAPI app with CORS, health check, and `/ask` endpoint.
  - Uses an async lifespan manager to initialize and dispose the `SkFoundryAgent`.
- **_logging_config.py**  
  - Centralizes Python `logging` setup for consistent structured logs.
- **_timing_middleware.py**  
  - Measures and logs request duration.

### 4.2 Service (Agent Layer)
- **_foundry_agent.py**  
  - Handles Azure credential resolution (`DefaultAzureCredential` or managed identity).
  - Creates an `AzureAIAgent` client and fetches the agent definition.
  - Streams responses, handles intermediate function calls/results.
  - Manages cleanup of HTTP sessions and credentials via `asynccontextmanager`.
- **sk_agent_service.py**  
  - Singleton façade used by FastAPI.
  - Lazily instantiates the `FoundryAgent` on first query.
  - Exposes a simple `ask(query: str) -> str` interface.

## 5. Data Flow

1. **Client** sends HTTP POST `/ask` with JSON `{ "query": "..." }`.
2. **FastAPI** (`engine/api.py`) receives request, logs start, and calls `await _agent_service.ask(query)`.
3. **SkFoundryAgent.ask**  
   - On first call, creates `FoundryAgent` via `FoundryAgent.create()`.
   - Passes the user prompt to `FoundryAgent.run()`.
4. **FoundryAgent.run**  
   - Invokes `AzureAIAgent.invoke_stream()` to get streaming responses.
   - Aggregates chunks, logs intermediate function calls/results.
5. **FastAPI** returns aggregated answer as `{ "answer": "..." }` and logs completion.

## 6. Configuration & Environment
- `.env` in `src/service/` holds:
  - `AZURE_AI_AGENT_ENDPOINT`
  - `AZURE_AI_AGENT_AGENT_ID`
  - Optional: `AZURE_CONTAINERAPP_CLIENT_ID`
- Local development uses `python-dotenv` to load `.env`.
- In Azure Container Apps or Functions or k8s based deploy, rely on managed identity.

## 7. Deployment Considerations
- Package as a container with:
  - Uvicorn launch command from `engine/api.py`.
  - Environment variables securely injected.
- Scale-out by container replication behind an ingress.

# Development setup

## Create conda env
```
conda env create -f conda.yml
conda activate sk_env
```

## Remove conda env
```
conda deactivate
conda env remove -n sk_env -y
```

## 0.1 Test

Test the sk orchestrate engine directly
```
./tests/test_sk_agents.sh
```

## 0.2 Test

Start the api server
```
./tests/start_api.sh
```

Test the api
```
./tests/test_sk_api.sh
```

## 0.3 Test in the docker
Update the docker/.env file SP credential details.

Build the docker instance
```
./dockers/start.sh
```

Test the api exposed in docker container
```
./tests/test_docker_api.sh
```

Stop the docker instance
```
./dockers/stop.sh
```

Prune the base image
```
docker image prune -f
docker images | grep sk
docker rmi <image-id> -f
```

## Deploy as container app
- create acr with basic at least
- grant the current user at least contributor or acrpull+acrpush roles
- for container app deploy: `az provider register -n Microsoft.App`

```
az upgrade
./containerapp/containerapp_deploy.sh
```

Test the container app endpoint
```
./tests/test_containerapp_api.sh
```

