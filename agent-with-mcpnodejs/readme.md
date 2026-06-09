## Agent With Node.js MCP Server

This sample demonstrates an end-to-end Model Context Protocol (MCP) setup using a Node.js/TypeScript MCP server, exposed over Streamable HTTP, and consumed from different client/agent patterns.

The project covers three main invocation paths:

```text
Agent Framework:
agent -> MCPStreamableHTTPTool -> MCP server

Foundry Agent:
agent -> MCP tool -> Foundry MCP connector -> MCP server

Curl/local test:
curl -> JSON-RPC body -> MCP server
```

## What this sample shows

This sample demonstrates:
- Node.js/TypeScript MCP server implementation
- MCP Streamable HTTP endpoint exposure
- MCP tool discovery using tools/list
- MCP tool invocation using tools/call
- Curl-based MCP validation
- Docker-based local validation
- Azure Container Apps hosting
- Agent Framework MCP client integration
- Foundry MCP connector integration
- Handled tool errors using CallToolResult
- Structured stdout logging

## Key Highlight: CallToolResult Response Shape

On the MCP server side, tool handlers should return an MCP-compatible CallToolResult shape.

- Success response example:

```
return {
  content: [
    {
      type: "text" as const,
      text: JSON.stringify(
        {
          success: true,
          data: result
        },
        null,
        2
      )
    }
  ],
  isError: false
};
```

- Handled tool/business error example:

```
return {
  content: [
    {
      type: "text" as const,
      text: JSON.stringify(
        {
          success: false,
          error: "Platform search was requested but this property is not CGPS/platform-enabled.",
          errorCode: "PLATFORM_SEARCH_NOT_ENABLED",
          _guidance: "Retry with searchMode: local."
        },
        null,
        2
      )
    }
  ],
  isError: true
};
```

**Note:**

Using this response shape helps avoid MCP client-side deserialization errors. Tool/ business errors remain visible to the agent as handled outcomes instead of becoming protocol-level failures.

## Agent framework flow
```
User prompt
  -> Agent Framework agent
  -> MCPStreamableHTTPTool
  -> MCP server
  -> MCP tool result
  -> Agent response
```

## Foundry flow
```
User prompt
  -> Foundry agent
  -> MCP tool
  -> Foundry MCP connector
  -> MCP server
  -> MCP tool result
  -> Agent response
```

## reference

- [mcp sdk support](https://modelcontextprotocol.io/docs/sdk)
- [ts mcp sdk](https://www.npmjs.com/package/@modelcontextprotocol/sdk)
- [ts mcp sdk examples](https://github.com/modelcontextprotocol/typescript-sdk)

