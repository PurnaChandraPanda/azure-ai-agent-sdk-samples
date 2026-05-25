#!/bin/bash

# Test health endpoint of local docker MCP server
echo "Testing local docker MCP server health endpoint..."
response=$(curl -v http://localhost:40028/healthz)
echo "Response from /healthz: $response"

# Test local docker MCP server
python -m tests.docker_client

echo "Local docker MCP server test completed."
