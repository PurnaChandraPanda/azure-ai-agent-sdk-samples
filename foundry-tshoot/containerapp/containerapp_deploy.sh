#!/bin/bash

set -e
# set -x

## <Pre-requisite> Resources defined in the script
RESOURCE_GROUP="rg-std2" # Resource group of acr, container app, etc.
ACR_NAME="regisry432pub47" # Supply the ACR resource name, e.g. "foundry1acr00042" 
LOCATION="eastus2" # Azure region where the resources are deployed, e.g. "eastus"
LOCAL_IMAGE_NAME="st_api" # Name of the local docker image, e.g. "sk_ui_api"
LOCAL_IMAGE_NAME_TAG="latest" # Tag for the local docker image, e.g. "v1" or "latest" or any ..
IMAGE_APP_PORT_NUMBER=8010 # Port number on which the app is running inside the container, i.e. find exposed port in dockers/Dockerfile, e.g. 4010
CONTAINERAPP_ENV_NAME="streaml8-env" # Name of the container app environment, e.g. "streamlit-env"
CONTAINERAPP_NAME="sl-tshoot-api" # Name of the container app, e.g. "streamlit-api"
USER_MANAGED_ID="uamiagent0005121" # User managed identity to pull the image from ACR, e.g. "uamiagent0001121"
FOUNDRY_RESOURCE_NAME="aifoundry3738" # Name of the Azure AI Foundry resource, e.g. "foundryeus00321"
ACA_SUBNET_ID="/subscriptions/6977e295-0d7c-4557-8e0b-26e2f6532103/resourceGroups/rg-eus2vnet45/providers/Microsoft.Network/virtualNetworks/eus2vnetabyo/subnets/default35"
COSMOS_ARM_ID="/subscriptions/6977e295-0d7c-4557-8e0b-26e2f6532103/resourceGroups/rg-std2/providers/Microsoft.DocumentDB/databaseAccounts/aifoundry3738cosmosdb" # ARM ID of the Cosmosb Account resource
## </Pre-requisite>

## 1) Build and tag the Docker image
docker build -t $LOCAL_IMAGE_NAME:$LOCAL_IMAGE_NAME_TAG -f dockers/Dockerfile .

## 2) Login to Azure Container Registry
az acr login -n $ACR_NAME -g $RESOURCE_GROUP

## 3) Tag the local image with the ACR login server
ACR_LOGIN_SERVER=$(az acr show \
                    --name $ACR_NAME \
                    -g $RESOURCE_GROUP \
                    --query loginServer \
                    --output tsv)
docker tag $LOCAL_IMAGE_NAME:$LOCAL_IMAGE_NAME_TAG $ACR_LOGIN_SERVER/$LOCAL_IMAGE_NAME:$LOCAL_IMAGE_NAME_TAG

## 4) Push the image to Azure Container Registry
docker push $ACR_LOGIN_SERVER/$LOCAL_IMAGE_NAME:$LOCAL_IMAGE_NAME_TAG

## 5) Delete the local docker image
docker rmi $LOCAL_IMAGE_NAME:$LOCAL_IMAGE_NAME_TAG -f
echo "removed local image: $LOCAL_IMAGE_NAME:$LOCAL_IMAGE_NAME_TAG"

docker rmi $ACR_LOGIN_SERVER/$LOCAL_IMAGE_NAME:$LOCAL_IMAGE_NAME_TAG -f
echo "removed local image: $ACR_LOGIN_SERVER/$LOCAL_IMAGE_NAME:$LOCAL_IMAGE_NAME_TAG"

## 6) Deploy the container app
### Create the container app environment if it doesn't exist
### Adding || true to swallow the failure if container app env does not exist
CONTAINERAPP_ENV_EXISTS=$(az containerapp env show \
                            --name $CONTAINERAPP_ENV_NAME \
                            --resource-group $RESOURCE_GROUP \
                            --query "name" \
                            --output tsv 2>/dev/null || true)
if [ -z "$CONTAINERAPP_ENV_EXISTS" ]; then
    echo "Creating container app environment: $CONTAINERAPP_ENV_NAME"

    # --internal-only: controls whether the environment itself is public-facing or internal/private; Internal environments have no public endpoints
    az containerapp env create \
        --name $CONTAINERAPP_ENV_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --infrastructure-subnet-resource-id $ACA_SUBNET_ID \
        --internal-only
else
  echo "Container app environment already exists: $CONTAINERAPP_ENV_NAME"
fi

## 7) Create the user managed identity if it doesn't exist
UAI_EXISTS=$(az identity show \
                --name $USER_MANAGED_ID \
                --resource-group $RESOURCE_GROUP \
                --query "name" \
                --output tsv 2>/dev/null || true)
if [ -z "$UAI_EXISTS" ]; then
    echo "Creating user managed identity: $USER_MANAGED_ID"
    az identity create \
        --name $USER_MANAGED_ID \
        --resource-group $RESOURCE_GROUP
else
    echo "User managed identity already exists: $USER_MANAGED_ID"
fi

## 7.1) Assign the user managed identity with acr pull role
### If the role is already assigned, then don't assign it again
UAI_PRINCIPAL_ID=$(az identity show \
                    --name $USER_MANAGED_ID \
                    --resource-group $RESOURCE_GROUP \
                    --query principalId -o tsv) 
ROLE_EXISTS=$(az role assignment list \
                --assignee-object-id $UAI_PRINCIPAL_ID \
                --role AcrPull \
                --scope $(az acr show -n $ACR_NAME -g $RESOURCE_GROUP --query id -o tsv) \
                --query "[?roleDefinitionName=='AcrPull']" \
                --output tsv)
if [ -z "$ROLE_EXISTS" ]; then
    echo "Assigning AcrPull role to user managed identity: $USER_MANAGED_ID"

    az role assignment create \
        --assignee-object-id $UAI_PRINCIPAL_ID \
        --role AcrPull \
        --scope $(az acr show -n $ACR_NAME -g $RESOURCE_GROUP --query id -o tsv)
else
    echo "AcrPull role already assigned to user managed identity: $USER_MANAGED_ID"
fi

## 7.2) Assign the user managed identity with Foundry User role on Foundry resource
### If the role is already assigned, then don't assign it again
FOUNDRY_ROLE_NAME="Foundry User"
ROLE_EXISTS=$(az role assignment list \
                --assignee-object-id $UAI_PRINCIPAL_ID \
                --role "$FOUNDRY_ROLE_NAME" \
                --scope $(az cognitiveservices account show -n $FOUNDRY_RESOURCE_NAME -g $RESOURCE_GROUP --query id -o tsv) \
                --query "[?roleDefinitionName=='$FOUNDRY_ROLE_NAME']" \
                --output tsv)
if [ -z "$ROLE_EXISTS" ]; then
    echo "Assigning $FOUNDRY_ROLE_NAME role to user managed identity: $USER_MANAGED_ID"
    
    az role assignment create \
        --assignee-object-id $UAI_PRINCIPAL_ID \
        --role "$FOUNDRY_ROLE_NAME" \
        --scope $(az cognitiveservices account show -n $FOUNDRY_RESOURCE_NAME -g $RESOURCE_GROUP --query id -o tsv)
else
    echo "$FOUNDRY_ROLE_NAME role already assigned to user managed identity: $USER_MANAGED_ID"
fi

## 7.3) Assign the user managed identity with Cosmos builtin data contributor role on Cosmos Account resource
### If the role is already assigned, then don't assign it again

# Cosmos DB built-in data contributor role
ROLE_DEFINITION_GUID="00000000-0000-0000-0000-000000000002"
ROLE_DEFINITION_ID="${COSMOS_ARM_ID}/sqlRoleDefinitions/${ROLE_DEFINITION_GUID}"

# Data access scope - "/" means account-level data-plane access.
DATA_SCOPE="/"

# Parse cosmos db account name, rg details
COSMOS_RG="${COSMOS_ARM_ID#*/resourceGroups/}"  # read everything after /resourceGroups/
COSMOS_RG="${COSMOS_RG%%/providers/*}"          # trim everything from /providers/
COSMOS_ACCOUNT_NAME="${COSMOS_ARM_ID##*/databaseAccounts/}"

# Check if data plane role already exists at root level - create otherwise
EXISTING_COUNT=$(az cosmosdb sql role assignment list \
  --account-name "$COSMOS_ACCOUNT_NAME" \
  --resource-group "$COSMOS_RG" \
  --query "[?principalId=='$UAI_PRINCIPAL_ID' && scope=='$COSMOS_ARM_ID' && ends_with(roleDefinitionId, '$ROLE_DEFINITION_GUID')] | length(@)" \
  -o tsv)
if [ "$EXISTING_COUNT" -gt 0 ]; then
    echo "Cosmos DB SQL data role assignment already exists - for $UAI_PRINCIPAL_ID on $COSMOS_ACCOUNT_NAME."
else
    echo "Creating Cosmos DB SQL data role assignment..."

    az cosmosdb sql role assignment create \
        --account-name "$COSMOS_ACCOUNT_NAME" \
        --resource-group "$COSMOS_RG" \
        --principal-id "$UAI_PRINCIPAL_ID" \
        --role-definition-id "$ROLE_DEFINITION_ID" \
        --scope "$DATA_SCOPE"

    echo "Role assignment created."
fi

## 8) Deploy the container app
### Adding || true to swallow the failure if container app does not exist
CONTAINERAPP_EXISTS=$(az containerapp show \
                        --name $CONTAINERAPP_NAME \
                        --resource-group $RESOURCE_GROUP \
                        --query "name" \
                        --output tsv 2>/dev/null || true)
if [ -z "$CONTAINERAPP_EXISTS" ]; then
    echo "Creating container app: $CONTAINERAPP_NAME"

    # Read the UAI id
    UAMI_ID=$(az identity show \
                --name $USER_MANAGED_ID \
                --resource-group $RESOURCE_GROUP \
                --query id -o tsv)

    # Read the UAI client id
    UAI_CLIENT_ID=$(az identity show \
                    --name $USER_MANAGED_ID \
                    --resource-group $RESOURCE_GROUP \
                    --query clientId -o tsv)

    # Create the container app with the specified parameters
    # Ensure the user managed identity is assigned to the container app and the image is pulled from the ACR
    ## Check that exposed port is same as target-port in container app
    ## ----- It's an internal Container Apps Environment. 
    ## With ingress "external": The app is exposed through the environment's inbound IP.
    ## Public internet: blocked
    ## VPN/VNet clients: allowed, if DNS/routing/NSG are correct
    ## ----- Other container apps: allowed
    az containerapp create \
        --name $CONTAINERAPP_NAME \
        --resource-group $RESOURCE_GROUP \
        --environment $CONTAINERAPP_ENV_NAME \
        --image $ACR_LOGIN_SERVER/$LOCAL_IMAGE_NAME:$LOCAL_IMAGE_NAME_TAG \
        --target-port $IMAGE_APP_PORT_NUMBER \
        --ingress external \
        --cpu 0.5 \
        --memory 1.0Gi \
        --min-replicas 1 \
        --max-replicas 3 \
        --user-assigned $UAMI_ID \
        --registry-server $ACR_LOGIN_SERVER \
        --registry-identity $UAMI_ID \
        --env-vars AZURE_CONTAINERAPP_CLIENT_ID=$UAI_CLIENT_ID
else
    echo "Container app already exists: $CONTAINERAPP_NAME"
fi

echo "Container app deployment completed successfully."
