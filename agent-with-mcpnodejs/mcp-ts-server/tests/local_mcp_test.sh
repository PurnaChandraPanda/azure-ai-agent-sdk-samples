
set -e

# test health endpoint
echo "### test health endpoint ###"
curl -v http://127.0.0.1:3000/health 

# test mcp initialize
echo "### test mcp initialize ###"
curl -sS -X POST http://127.0.0.1:3000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-06-18",
      "capabilities": {},
      "clientInfo": {
        "name": "curl-test-client",
        "version": "1.0.0"
      }
    }
  }' | jq

# test tools/list
echo "### test tools/list ###"
curl -sS -X POST http://127.0.0.1:3000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }' | jq

# test tool call
echo "### test tool call ###"
curl -sS -X POST http://127.0.0.1:3000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "player_query",
      "arguments": {
        "action": "search_players",
        "searchQuery": "John",
        "searchType": "firstName"
      }
    }
  }' | jq

## test handled error in tool call
echo "### test handled error in tool call ###"
curl -sS -X POST http://127.0.0.1:3000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "teetime_action",
      "arguments": {
        "action": "search_teetimes",
        "propertyId": "PROP-001",
        "searchMode": "platform"
      }
    }
  }' | jq

## test tool call: success
echo "### test tool call: success ###"
curl -sS -X POST http://127.0.0.1:3000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "teetime_action",
      "arguments": {
        "action": "search_teetimes",
        "propertyId": "PROP-001",
        "searchMode": "local"
      }
    }
  }' | jq -r '.result.content[0].text' | jq


## Test booking error: existing player missing extProfileId
echo "### Test booking error: existing player missing extProfileId ###"
curl -sS -X POST http://127.0.0.1:3000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "tools/call",
    "params": {
      "name": "teetime_action",
      "arguments": {
        "action": "book_teetime",
        "propertyId": "PROP-001",
        "teeTimeId": "TT-9001",
        "players": [
          {
            "playerType": "existing",
            "firstName": "John",
            "lastName": "Doe"
          }
        ]
      }
    }
  }' | jq


## Test booking success
echo "### Test booking success ###"
curl -sS -X POST http://127.0.0.1:3000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 7,
    "method": "tools/call",
    "params": {
      "name": "teetime_action",
      "arguments": {
        "action": "book_teetime",
        "propertyId": "PROP-001",
        "teeTimeId": "TT-9001",
        "players": [
          {
            "playerType": "existing",
            "extProfileId": "EXT-1001"
          },
          {
            "playerType": "guest",
            "firstName": "Guest",
            "lastName": "One"
          }
        ]
      }
    }
  }' | jq -r '.result.content[0].text' | jq


