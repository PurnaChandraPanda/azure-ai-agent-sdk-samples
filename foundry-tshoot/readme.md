Troubleshoot connectivity for standard foundry agents.

## Details
Designed it as a plugin-style diagnostic framework:
- Common network checks: DNS, TCP, TLS, HTTP
- Common auth: DefaultAzureCredential
- Service-specific plugins:
    - Cosmos DB
    - Storage Blob
    - Azure AI Search
    - Later: Key Vault, Event Hub, Service Bus, Azure OpenAI, Foundry endpoints, etc.

Streamlit UI dynamically renders plugins from a registry.


## Create conda env
```
conda env create -f conda.yml
conda activate st_env
```

## Remove conda env
```
conda deactivate
conda env remove -n st_env -y
```

## Dev test

```
conda activate st_env
```

```
pip install pytest
```

```
PYTHONPATH=src pytest tests/test_models.py

PYTHONPATH=src pytest tests/test_network.py

PYTHONPATH=src pytest tests/test_cosmos_plugin.py
```

```
RUN_LIVE_COSMOS_TESTS=1 \
COSMOS_ENDPOINT="https://aifoundry3738cosmosdb.documents.azure.com:443/" \
COSMOS_DATABASE="enterprise_memory" \
COSMOS_CONTAINER="2f48551e-5805-4ed7-b0b6-aa98c259fda9-agent-entity-store" \
COSMOS_HEALTH_ITEM_ID="ent_msg_cihhz8056NjehVydyT6FqBEj" \
COSMOS_HEALTH_PARTITION_KEY="2f48551e-5805-4ed7-b0b6-aa98c259fda9_2026_03" \
PYTHONPATH=src pytest tests/test_cosmos_live.py
```


## Confirm that the code can be run fine in local docker
Build the docker instance
```
cd foundry-tshoot (if not already in this folder)
./dockers/start.sh
```

Test out the UI app over 40000 port (for local test)

Stop the docker instance
```
cd foundry-tshoot (if not already in this folder)
./dockers/stop.sh
```

## Deploy the container app

**Pre-requisite**
- Get local docker app running first for a test
- Have resources pre-created: 1) ACR, 2) AI Foundry
- Remember to feed in the variables defined in `containerapp_deploy.sh`
- Run the script to perform container app deploy action

```
cd foundry-tshoot (if not already in this folder)
az upgrade
./containerapp/containerapp_deploy.sh
```

## Cleanup container app

```
./containerapp/containerapp_cleanup.sh
```

