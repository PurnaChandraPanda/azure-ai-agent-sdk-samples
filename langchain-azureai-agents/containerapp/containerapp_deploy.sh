#!/bin/bash

set -e
# set -x

## Resources defined
RESOURCE_GROUP="" # Resource group of acr, container app, etc.
ACR_NAME=""
LOCATION=""
LOCAL_IMAGE_NAME="langchain_api"
LOCAL_IMAGE_NAME_TAG="latest"
CONTAINERAPP_NAME="langhcain2-api"
CONTAINERAPP_ENV_NAME="langchain2-env"
USER_MANAGED_ID="" # User managed identity to pull the image from ACR
FOUNDRY_RESOURCE_NAME="" # Name of the Azure AI Foundry resource


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

## 7.2) Assign the user managed identity Azure AI User role on Foundry resource
### If the role is already assigned, then don't assign it again
ROLE_EXISTS=$(az role assignment list \
                --assignee-object-id $UAI_PRINCIPAL_ID \
                --role "Azure AI User" \
                --scope $(az cognitiveservices account show -n $FOUNDRY_RESOURCE_NAME -g $RESOURCE_GROUP --query id -o tsv) \
                --query "[?roleDefinitionName=='Azure AI User']" \
                --output tsv)
if [ -z "$ROLE_EXISTS" ]; then
    echo "Assigning Azure AI User role to user managed identity: $USER_MANAGED_ID"
    
    az role assignment create \
        --assignee-object-id $UAI_PRINCIPAL_ID \
        --role "Azure AI User" \
        --scope $(az cognitiveservices account show -n $FOUNDRY_RESOURCE_NAME -g $RESOURCE_GROUP --query id -o tsv)
else
    echo "Azure AI User role already assigned to user managed identity: $USER_MANAGED_ID"
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
    az containerapp create \
        --name $CONTAINERAPP_NAME \
        --resource-group $RESOURCE_GROUP \
        --environment $CONTAINERAPP_ENV_NAME \
        --image $ACR_LOGIN_SERVER/$LOCAL_IMAGE_NAME:$LOCAL_IMAGE_NAME_TAG \
        --target-port 4000 \
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
