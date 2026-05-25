
https://pypi.org/project/mcp
https://github.com/modelcontextprotocol/python-sdk/issues/1383

## Transports in MCP
- MCP uses JSON-RPC to encode messages. JSON-RPC messages MUST be UTF-8 encoded.
- The protocol currently defines [two standard transport mechanisms](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports) for client-server communication:
    - `stdio`, communication over standard in and standard out
    - `Streamable HTTP`

- MCP with sampling - https://github.com/modelcontextprotocol/python-sdk/blob/main/examples/snippets/servers/sampling.py

## Run local MCP server
```
cd mcp-sampling-server
python -m src.server
```

**output**
```
2026-01-17 07:01:30,716 [server] : INFO     [13968] Health API started on http://127.0.0.1:8001/healthz
INFO:     Started server process [13968]
INFO:     Waiting for application startup.
StreamableHTTP session manager started
INFO:     Application startup complete.
INFO:     Started server process [13968]
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     127.0.0.1:56386 - "GET /healthz HTTP/1.1" 200 OK
Created new transport with session ID: 842f3995e38b40a7ab857eb35467f54e
INFO:     127.0.0.1:53926 - "POST /mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:53926 - "POST /mcp HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:53942 - "GET /mcp HTTP/1.1" 200 OK
Processing request of type ListToolsRequest
INFO:     127.0.0.1:53946 - "POST /mcp HTTP/1.1" 200 OK
Processing request of type CallToolRequest
2026-01-17 07:04:34,042 [server] : INFO     [13968] add(): 2 and 3
2026-01-17 07:04:34,043 [server] : INFO     [13968] add() result: 5
INFO:     127.0.0.1:53946 - "POST /mcp HTTP/1.1" 200 OK
Terminating session: 842f3995e38b40a7ab857eb35467f54e
INFO:     127.0.0.1:53946 - "DELETE /mcp HTTP/1.1" 200 OK
```

## Run local MCP client tests
```
cd mcp-sampling-server
tests/consume_local_mcp.sh
```

**output**
```
Response from /healthz: {"status":"ok","service":"mcp"}
Available tools: ['add']
Add tool input schema: {
  "properties": {
    "a": {
      "title": "A",
      "type": "integer"
    },
    "b": {
      "title": "B",
      "type": "integer"
    }
  },
  "required": [
    "a",
    "b"
  ],
  "title": "addArguments",
  "type": "object"
}
Result (text): 5
```
