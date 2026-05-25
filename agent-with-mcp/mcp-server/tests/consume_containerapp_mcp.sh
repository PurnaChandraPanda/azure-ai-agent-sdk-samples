#!/bin/bash

set -e

## Resources defined
RESOURCE_GROUP="rg-foundry1eus" # Resource group of container app
LOCATION="eastus"
CONTAINERAPP_NAME="mcpserver8-api"

## Set the numbers for load test
total_requests=1
sleep_duration=0.5

## 1) For the container app, get its URL
CONTAINERAPP_FQDN=$(az containerapp show \
                    --name $CONTAINERAPP_NAME \
                    --resource-group $RESOURCE_GROUP \
                    --query "properties.configuration.ingress.fqdn" \
                    --output tsv)

CONTAINERAPP_URL="https://$CONTAINERAPP_FQDN"

echo "Container App URL: $CONTAINERAPP_URL"

MCP_API="$CONTAINERAPP_URL/mcp"

# Make it visible to the child processes of the script (in python)
export MCP_API

## 2) Test the container app endpoint

# Run the curl test script in a loop N times with a delay of x seconds each time
for i in $(seq 1 "$total_requests");
do
    echo "Running iteration $i"
    python -m tests.aca_client
    echo ""
    sleep $sleep_duration
done

echo "All iterations completed."


## View logs in the container app
## Option 0)
# az containerapp logs show \
#   --name $CONTAINERAPP_NAME \
#   --resource-group $RESOURCE_GROUP

## Option 1)
# Go to azure portal -> contianr apps -> Monitoring -> Log stream
# Select the container app> and view logs as app is used

## Option 2)
# Go to azure portal -> contianr apps -> Monitoring -> Logs
# In the query editor, query table `ContainerAppConsoleLogs_CL`

