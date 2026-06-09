import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

export type AppPayload = Record<string, unknown>;

export function createToolResponse(
  success: boolean,
  payload: AppPayload,
  isError = !success
): CallToolResult {
  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify(
          {
            success,
            ...payload
          },
          null,
          2
        )
      }
    ],
    isError
  };
}

export function createToolError(
  error: string,
  errorCode: string,
  guidance?: string,
  extra?: AppPayload
): CallToolResult {
  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify(
          {
            success: false,
            error,
            errorCode,
            ...(guidance ? { _guidance: guidance } : {}),
            ...(extra ?? {})
          },
          null,
          2
        )
      }
    ],
    isError: true
  };
}

export function createPlayerLookupGuidance(playerNumber: number): string {
  return [
    `ASK user: "How would you like to search for Player ${playerNumber}? Options: first name, last name, full name, email, phone number, or patron ID"`,
    "",
    "Search options available:",
    "  • firstName - First name",
    "  • lastName - Last name",
    "  • fullName - Full name",
    "  • email - Email address",
    "  • phoneNumber - Phone number",
    "  • patronId - Patron/loyalty ID",
    "",
    "Example MCP tool calls:",
    '  • First name: player_query { action: "search_players", searchQuery: "John", searchType: "firstName" }',
    '  • Email: player_query { action: "search_players", searchQuery: "john.doe@example.com", searchType: "email" }',
    '  • Phone: player_query { action: "search_players", searchQuery: "5551234567", searchType: "phoneNumber" }',
    "",
    "If the search result is an EXTERNAL profile and has extProfileId, pass extProfileId into teetime_action players[].extProfileId to book."
  ].join("\n");
}

