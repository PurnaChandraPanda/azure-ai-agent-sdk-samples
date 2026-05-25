## Sampling in MCP

- `MCP Samping` is a protocol feature that lets an MCP server ask the MCP client to run an LLM generation (a `completion`) and return the result back to the server.

- Sampling = server-initiated request for an LLM generation via the client.
- The MCP server sends a `sampling/createMessage` request; the client uses an LLM, runs the generation, and returns the output.
- This design exists so that LLM access, model choice, and permissions stay controlled by the client, while the server can still `borrow` intelligence when needed - without the server holding any model API keys. 

## Sampling - what happens on the wire

- Your client calls a tool on the MCP server.
- Inside that tool, the server does `await ctx.session.create_message(..SamplingMessage(content)..)` (MCP) or `await ctx.sample(...)` (FastMCP) to request an LLM completion. 
- That becomes an MCP JSON-RPC request to the client: `sampling/createMessage`.
- Your client's `sampling_callback` runs, calls the LLM provider (Azure OpenAI / OpenAI / Anthropic / local), and returns a `CreateMessageResult`.
- Server continues the tool and returns the final tool output to the client.

## Create conda env
```
conda env create -f mcp-sampling-server/conda.yml
conda activate mcp_env
```

## Remove conda env
```
conda deactivate
conda env remove -n mcp_env -y
```





