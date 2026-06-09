import express from "express";
import cors from "cors";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { createMcpServer } from "./mcp/server.js";
import {
  handlePlayerQuery,
  handleTeeTimeAction
} from "./mcp/tools.js";
import { logError, logInfo, logWarn } from "./logger.js";

const app = express();

app.use(express.json({ limit: "1mb" }));

app.use(
  cors({
    origin: true,
    exposedHeaders: ["mcp-session-id"],
    allowedHeaders: ["Content-Type", "Accept", "mcp-session-id"]
  })
);

const PORT = Number(process.env.PORT ?? 3000);
const HOST = process.env.HOST ?? "127.0.0.1";


/**
 * Generic HTTP request logging.
 * This will log every request, including /health and /mcp.
 */
app.use((req, res, next) => {
  const start = Date.now();

  res.on("finish", () => {
    logInfo("HTTP request completed", {
      method: req.method,
      path: req.originalUrl,
      statusCode: res.statusCode,
      durationMs: Date.now() - start
    });
  });

  next();
});


app.post("/mcp", async (req, res) => {
  const start = Date.now();

  const rpcId = req.body?.id ?? null;
  const rpcMethod = req.body?.method ?? "unknown";
  const toolName = req.body?.params?.name;
  const toolArguments = req.body?.params?.arguments;

  logInfo("MCP request received", {
    rpcId,
    rpcMethod,
    toolName,
    hasArguments: toolArguments !== undefined
  });

  if (rpcMethod === "tools/call") {
    logInfo("MCP tool call received", {
      rpcId,
      toolName,
      arguments: toolArguments
    });
  }

  try {
    const server = createMcpServer();

    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
      enableJsonResponse: true
    });

    res.on("close", () => {
      logInfo("MCP response connection closed", {
        rpcId,
        rpcMethod,
        toolName,
        durationMs: Date.now() - start
      });

      transport.close();
      server.close();
    });

    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);

    logInfo("MCP request handled", {
      rpcId,
      rpcMethod,
      toolName,
      durationMs: Date.now() - start
    });
  } catch (error) {
    logError("MCP request failed", error, {
      rpcId,
      rpcMethod,
      toolName,
      durationMs: Date.now() - start
    });

    if (!res.headersSent) {
      res.status(500).json({
        jsonrpc: "2.0",
        error: {
          code: -32603,
          message: "Internal server error",
          data: {
            message: error instanceof Error ? error.message : String(error)
          }
        },
        id: rpcId
      });
    }
  }
});


app.get("/health", (_req, res) => {
  res.json({
    status: "ok",
    service: "demo-teetime-mcp-server",
    transport: "streamable-http",
    mode: "stateless"
  });
});

app.post("/mcp", async (req, res) => {
  const start = Date.now();

  const rpcId = req.body?.id ?? null;
  const rpcMethod = req.body?.method ?? "unknown";
  const toolName = req.body?.params?.name;
  const toolArgs = req.body?.params?.arguments;

  logInfo("MCP request received", {
    rpcId,
    rpcMethod,
    toolName,
    hasArguments: toolArgs !== undefined
  });

  if (rpcMethod === "tools/call") {
    logInfo("MCP tool call received", {
      rpcId,
      toolName,
      arguments: toolArgs
    });
  }

  try {
    const server = createMcpServer();

    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
      enableJsonResponse: true
    });

    res.on("close", () => {
      logInfo("MCP response connection closed", {
        rpcId,
        rpcMethod,
        toolName,
        durationMs: Date.now() - start
      });

      transport.close();
      server.close();
    });

    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);

    logInfo("MCP request handled", {
      rpcId,
      rpcMethod,
      toolName,
      durationMs: Date.now() - start
    });
  } catch (error) {
    logError("MCP request failed", error, {
      rpcId,
      rpcMethod,
      toolName,
      durationMs: Date.now() - start
    });

    if (!res.headersSent) {
      res.status(500).json({
        jsonrpc: "2.0",
        error: {
          code: -32603,
          message: "Internal server error",
          data: {
            message: error instanceof Error ? error.message : String(error)
          }
        },
        id: rpcId
      });
    }
  }
});


app.get("/mcp", (_req, res) => {
  res.status(405).json({
    error:
      "GET /mcp is not enabled in this stateless JSON response sample. Use POST /mcp."
  });
});

app.delete("/mcp", (_req, res) => {
  res.status(405).json({
    error:
      "DELETE /mcp is not enabled in this stateless JSON response sample. Use POST /mcp."
  });
});

/**
 * Optional REST-like wrappers for quick local testing.
 * These are not MCP standard endpoints.
 * Your real MCP clients should call POST /mcp.
 */
app.post("/api/tools/player_query", async (req, res) => {
  const result = await handlePlayerQuery(req.body);
  res.status(result.isError ? 400 : 200).json(result);
});

app.post("/api/tools/teetime_action", async (req, res) => {
  const result = await handleTeeTimeAction(req.body);
  res.status(result.isError ? 400 : 200).json(result);
});

app.listen(PORT, HOST, () => {
  logInfo("MCP server started", {
      host: HOST,
      port: PORT,
      mcpEndpoint: `http://${HOST}:${PORT}/mcp`,
      healthEndpoint: `http://${HOST}:${PORT}/health`,
      logLevel: process.env.LOG_LEVEL ?? "info"
  });
});

