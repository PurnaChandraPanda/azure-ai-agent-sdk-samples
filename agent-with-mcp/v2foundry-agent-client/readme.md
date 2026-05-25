
## create/ activate conda env for local test

```
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

conda create -n v2foundry python=3.10 -y
```

```
conda activate v2foundry
python --version
```

## install foundry packages
```
pip install azure-ai-projects==2.0.0b3
pip install python-dotenv
pip install aiohttp
```

## run
python -m src.0_create_agent
python -m src.1_interact_agent

## references

https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_mcp_async.py


