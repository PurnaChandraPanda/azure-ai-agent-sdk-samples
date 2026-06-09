import { z } from "zod";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import {
  dummyPlayers,
  dummyPropertyConfig,
  dummyTeeTimes
} from "../data/dummyData.js";
import {
  createPlayerLookupGuidance,
  createToolError,
  createToolResponse
} from "./responses.js";

export const PlayerQueryInputSchema = {
  action: z.enum(["search_players"]),
  searchQuery: z.string().min(1),
  searchType: z.enum([
    "firstName",
    "lastName",
    "fullName",
    "email",
    "phoneNumber",
    "patronId"
  ])
};

export const TeeTimeActionInputSchema = {
  action: z.enum(["search_teetimes", "book_teetime"]),
  propertyId: z.string().min(1),
  searchMode: z.enum(["local", "platform"]).optional(),
  teeTimeId: z.string().optional(),
  players: z
    .array(
      z.object({
        playerType: z.enum(["existing", "guest"]),
        firstName: z.string().optional(),
        lastName: z.string().optional(),
        extProfileId: z.string().optional()
      })
    )
    .optional()
};

export async function handlePlayerQuery(args: {
  action: "search_players";
  searchQuery: string;
  searchType:
    | "firstName"
    | "lastName"
    | "fullName"
    | "email"
    | "phoneNumber"
    | "patronId";
}): Promise<CallToolResult> {
  const query = args.searchQuery.trim().toLowerCase();

  const results = dummyPlayers.filter((player) => {
    switch (args.searchType) {
      case "firstName":
        return player.firstName.toLowerCase().includes(query);

      case "lastName":
        return player.lastName.toLowerCase().includes(query);

      case "fullName":
        return `${player.firstName} ${player.lastName}`
          .toLowerCase()
          .includes(query);

      case "email":
        return player.email.toLowerCase().includes(query);

      case "phoneNumber":
        return player.phoneNumber.includes(args.searchQuery.trim());

      case "patronId":
        return player.patronId.toLowerCase() === query;

      default:
        return false;
    }
  });

  if (results.length === 0) {
    return createToolError(
      "No matching players found.",
      "PLAYER_NOT_FOUND",
      "Ask the user to try another search type or provide more accurate player information.",
      {
        searchType: args.searchType,
        searchQuery: args.searchQuery
      }
    );
  }

  return createToolResponse(true, {
    action: args.action,
    matchCount: results.length,
    results,
    nextStep:
      "Use the selected player's extProfileId in teetime_action players[].extProfileId."
  });
}

export async function handleTeeTimeAction(args: {
  action: "search_teetimes" | "book_teetime";
  propertyId: string;
  searchMode?: "local" | "platform";
  teeTimeId?: string;
  players?: Array<{
    playerType: "existing" | "guest";
    firstName?: string;
    lastName?: string;
    extProfileId?: string;
  }>;
}): Promise<CallToolResult> {
  if (args.propertyId !== dummyPropertyConfig.propertyId) {
    return createToolError(
      `Unknown propertyId '${args.propertyId}'.`,
      "PROPERTY_NOT_FOUND",
      `Use propertyId '${dummyPropertyConfig.propertyId}' for this dummy server.`
    );
  }

  if (args.searchMode === "platform" && !dummyPropertyConfig.isCgpsEnabled) {
    return createToolError(
      "Platform search was requested but this property is not CGPS/platform-enabled (propConfig.ISCGPSENABLED is false). Use local search or enable CGPS for this property.",
      "PLATFORM_SEARCH_NOT_ENABLED",
      "Retry with searchMode: local, or enable CGPS/platform search for this property.",
      {
        propertyId: dummyPropertyConfig.propertyId,
        propertyName: dummyPropertyConfig.propertyName,
        isCgpsEnabled: dummyPropertyConfig.isCgpsEnabled
      }
    );
  }

  if (args.action === "search_teetimes") {
    return createToolResponse(true, {
      propertyId: dummyPropertyConfig.propertyId,
      propertyName: dummyPropertyConfig.propertyName,
      searchMode: args.searchMode ?? "local",
      teeTimes: dummyTeeTimes
    });
  }

  if (!args.teeTimeId) {
    return createToolError(
      "teeTimeId is required for booking.",
      "TEETIME_ID_REQUIRED",
      "First call teetime_action with action: search_teetimes, then pass the selected teeTimeId into action: book_teetime."
    );
  }

  const selectedTeeTime = dummyTeeTimes.find(
    (teeTime) => teeTime.teeTimeId === args.teeTimeId
  );

  if (!selectedTeeTime) {
    return createToolError(
      `Tee time '${args.teeTimeId}' was not found.`,
      "TEETIME_NOT_FOUND",
      "Call teetime_action with action: search_teetimes to get valid teeTimeId values."
    );
  }

  if (!args.players || args.players.length === 0) {
    return createToolError(
      "At least one player is required to book a tee time.",
      "PLAYERS_REQUIRED",
      "Pass players[] with either guest player details or existing player extProfileId."
    );
  }

  const existingPlayerIndexMissingLookup = args.players.findIndex(
    (player) => player.playerType === "existing" && !player.extProfileId
  );

  if (existingPlayerIndexMissingLookup >= 0) {
    const playerNumber = existingPlayerIndexMissingLookup + 1;

    return createToolError(
      `Player ${playerNumber} (Existing Player) requires player lookup.`,
      "PLAYER_LOOKUP_REQUIRED",
      createPlayerLookupGuidance(playerNumber),
      {
        playerNumber,
        missingField: `players[${existingPlayerIndexMissingLookup}].extProfileId`
      }
    );
  }

  const bookingId = `BKG-${Math.floor(100000 + Math.random() * 900000)}`;

  return createToolResponse(true, {
    bookingId,
    status: "CONFIRMED",
    propertyId: dummyPropertyConfig.propertyId,
    propertyName: dummyPropertyConfig.propertyName,
    teeTime: selectedTeeTime,
    players: args.players,
    message: "Tee time booked successfully using dummy data."
  });
}