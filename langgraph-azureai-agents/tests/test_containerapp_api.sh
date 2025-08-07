#!/bin/bash

set -e

## Resources defined
RESOURCE_GROUP="rg-foundry1eus" # Resource group of container app
LOCATION="eastus"
CONTAINERAPP_NAME="langgraph-api"

## Set the numbers for load test
total_requests=20
sleep_duration=0.5

## 1) For the container app, get its URL
CONTAINERAPP_FQDN=$(az containerapp show \
                    --name $CONTAINERAPP_NAME \
                    --resource-group $RESOURCE_GROUP \
                    --query "properties.configuration.ingress.fqdn" \
                    --output tsv)

CONTAINERAPP_URL="https://$CONTAINERAPP_FQDN"

echo "Container App URL: $CONTAINERAPP_URL"

## 2) Test the container app endpoint

# Run the curl test script in a loop N times with a delay of x seconds each time
for i in $(seq 1 "$total_requests");
do
    echo "Running iteration $i"
    response=$(curl --silent --show-error --no-keepalive \
            -H "Connection: close" \
            -H "Content-Type: application/json" \
            -X POST $CONTAINERAPP_URL/ask \
            -d '{"query":"5 supply chain news for microsoft"}' \
            -w '\n%{time_total}\n')
    
    time_taken=$(printf '%s\n' "$response" | tail -n1)
    body=$(printf '%s\n' "$response" | sed '$d')

    echo "Response: $body"
    echo "Time taken: ${time_taken}s"
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

