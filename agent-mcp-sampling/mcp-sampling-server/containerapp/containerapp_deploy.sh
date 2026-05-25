#!/bin/bash

set -e
# set -x

## <Pre-requisite> Resources defined in the script
SUBSCRIPTION_ID="697--------------------2103" # Azure subscription ID - e.g. "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
RESOURCE_GROUP="rg-foundry1eus" # Resource group of acr, container app, etc. - e.g. "rg-foundry1eus"
ACR_NAME="foundry1acr00042" # ACR resource name - e.g. "foundry1acr00042"
LOCATION="eastus" # Location for Azure resources - e.g. "eastus"
LOCAL_IMAGE_NAME="mcpserver_api_base" # Local docker image name - e.g. "skapp_api"
LOCAL_IMAGE_NAME_TAG="latest" # Local docker image tag - e.g. "latest"
IMAGE_MCP_APP_PORT_NUMBER=8000 # Port number on which the MCP app is running inside the container
IMAGE_HEALTH_PROBE_PORT_NUMBER=8001 # Port number for health probe inside the container
CONTAINERAPP_ENV_NAME="mcpserver-env" # Container app environment resource name - e.g. "skapp-env"
CONTAINERAPP_NAME="mcpserver8-api" # Container app resource name - e.g. "skapp-api"
USER_MANAGED_ID="uamiagent0001121" # User managed identity to pull the image from ACR - e.g. "uamiagent0001121"
FOUNDRY_RESOURCE_NAME="foundryeus00321" # Name of the Azure AI Foundry resource - e.g. "foundryeus00321"
ACA_TEMPLATE_FILE="containerapp/containerapp.template.yml" # Path to the container app template file

# User container spec details
MIN_REPLICAS=1
MAX_REPLICAS=3
CPU="0.5"
MEMORY="1Gi"
## </Pre-requisite>

## 0) Set the Azure subscription context
az login --identity
az account set --subscription $SUBSCRIPTION_ID

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

## 5) Delete the local docker images
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

    az containerapp env create \
        --name $CONTAINERAPP_ENV_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION
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

## 7.1) Assign the user managed identity acr pull role
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

# ## 7.2) Assign the user managed identity Azure AI User role on Foundry resource
# ### If the role is already assigned, then don't assign it again
# ROLE_EXISTS=$(az role assignment list \
#                 --assignee-object-id $UAI_PRINCIPAL_ID \
#                 --role "Azure AI User" \
#                 --scope $(az cognitiveservices account show -n $FOUNDRY_RESOURCE_NAME -g $RESOURCE_GROUP --query id -o tsv) \
#                 --query "[?roleDefinitionName=='Azure AI User']" \
#                 --output tsv)
# if [ -z "$ROLE_EXISTS" ]; then
#     echo "Assigning Azure AI User role to user managed identity: $USER_MANAGED_ID"
    
#     az role assignment create \
#         --assignee-object-id $UAI_PRINCIPAL_ID \
#         --role "Azure AI User" \
#         --scope $(az cognitiveservices account show -n $FOUNDRY_RESOURCE_NAME -g $RESOURCE_GROUP --query id -o tsv)
# else
#     echo "Azure AI User role already assigned to user managed identity: $USER_MANAGED_ID"
# fi

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
    
    # Read container app environment id
    CONTAINERAPP_ENV_ID=$(az containerapp env show \
                                    -g "$RESOURCE_GROUP" \
                                    -n "$CONTAINERAPP_ENV_NAME" \
                                    --query id -o tsv)

    # Create the container app with the specified parameters
    # Ensure the user managed identity is assigned to the container app and the image is pulled from the ACR
    ## Check that exposed port is same as target-port in container app

    # Export the variables to be used in envsubst
    export CONTAINERAPP_NAME LOCATION UAI_CLIENT_ID UAMI_ID IMAGE_MCP_APP_PORT_NUMBER IMAGE_HEALTH_PROBE_PORT_NUMBER ACR_LOGIN_SERVER LOCAL_IMAGE_NAME LOCAL_IMAGE_NAME_TAG CONTAINERAPP_ENV_ID MIN_REPLICAS MAX_REPLICAS CPU MEMORY

    # Substitute variable into a temp file for container app yaml
    envsubst < $ACA_TEMPLATE_FILE > containerapp.yml

    # Deploy the container app using the yaml file
    az containerapp create \
        --name $CONTAINERAPP_NAME \
        --resource-group $RESOURCE_GROUP \
        --yaml containerapp.yml
    
    # Optionally, delete the generated yaml file
    rm containerapp.yml
else
    echo "Container app already exists: $CONTAINERAPP_NAME"
fi

echo "Container app deployment completed successfully."
