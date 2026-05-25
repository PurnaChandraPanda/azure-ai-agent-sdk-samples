
## create/ activate conda env for local test

```
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

conda create -n agentfx python=3.10 -y
```

```
conda activate agentfx
python --version
```

pip install agent-framework
####pip install agent-framework-azure-ai --pre


https://github.com/microsoft/agent-framework/blob/main/python/samples/getting_started/agents/azure_ai/README.md

---

- In MCP, `Prompts` are a separate capability from `Tools`. Prompts are discovered via [prompts/list](https://modelcontextprotocol.io/specification/2025-06-18/server/prompts) and retrieved via prompts/get, and their "inputs" are described as an arguments list, not a JSON Schema parameters object. 
- OpenAI function tools require `tools[].parameters` to be a valid `JSON Schema object` (and definitely not None). When agent-framework tries to map an MCP prompt into an OpenAI tool, it can end up with parameters=None or include null in places where OpenAI expects a string.
- Agent Framework passes MCP capabilities as OpenAI function tools. OpenAI strictly validates each function's parameters schema.



