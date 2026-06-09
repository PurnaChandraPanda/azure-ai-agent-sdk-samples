
## Setup env
- Before running the Foundry sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.

- Rename `.env.example` to `.env`
- Update the env variable values

## How to run

- create agent
```
python 0_create_foundry_mcp_agent.py
```

- run agent
```
python 1_run_foundry_mcp_agent.py
```
