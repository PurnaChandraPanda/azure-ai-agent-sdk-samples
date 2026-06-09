import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import {
  handlePlayerQuery,
  handleTeeTimeAction,
  PlayerQueryInputSchema,
  TeeTimeActionInputSchema
} from "./tools.js";

export function createMcpServer(): McpServer {
  const server = new McpServer({
    name: "demo-teetime-mcp-server",
    version: "1.0.0"
  });

  server.registerTool(
    "player_query",
    {
      title: "Player Query",
      description:
        "Search existing player profiles by first name, last name, full name, email, phone number, or patron ID.",
      inputSchema: PlayerQueryInputSchema
    },
    async (args) => {
      return handlePlayerQuery(args);
    }
  );

  server.registerTool(
    "teetime_action",
    {
      title: "Tee Time Action",
      description:
        "Search tee times or book a tee time. Existing players require extProfileId from player_query before booking.",
      inputSchema: TeeTimeActionInputSchema
    },
    async (args) => {
      return handleTeeTimeAction(args);
    }
  );

  return server;
}

