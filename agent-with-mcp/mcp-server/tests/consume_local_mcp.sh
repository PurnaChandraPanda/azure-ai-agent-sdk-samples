#!/bin/bash

# Test health endpoint of local MCP server
echo "Testing local MCP server health endpoint..."
response=$(curl -v http://localhost:8001/healthz)
echo "Response from /healthz: $response"

# Test local MCP server
python -m tests.local_client

echo "Local MCP server test completed."
