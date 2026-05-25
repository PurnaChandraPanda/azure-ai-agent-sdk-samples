#!/bin/bash

set -euo pipefail
# set -x

## <Config>
RESOURCE_GROUP="rg-std2"
ACR_NAME="regisry432pub47"
LOCAL_IMAGE_NAME="st_api"
LOCAL_IMAGE_NAME_TAG="latest"

CONTAINERAPP_ENV_NAME="streaml8-env"
CONTAINERAPP_NAME="sl-tshoot-api"
USER_MANAGED_ID="uamiagent0005121"
FOUNDRY_RESOURCE_NAME="aifoundry3738"

COSMOS_ARM_ID="/subscriptions/6977e295-0d7c-4557-8e0b-26e2f6532103/resourceGroups/rg-std2/providers/Microsoft.DocumentDB/databaseAccounts/aifoundry3738cosmosdb"

# Safer defaults.
# Set to true only if these were created only for this deployment.
DELETE_CONTAINERAPP_ENV=true
DELETE_USER_MANAGED_ID=true

# Usually safe if this image/tag was created only by this script.
DELETE_ACR_IMAGE=true
## </Config>


echo "Starting cleanup..."


## Parse Cosmos details
COSMOS_RG="${COSMOS_ARM_ID#*/resourceGroups/}"
COSMOS_RG="${COSMOS_RG%%/providers/*}"
COSMOS_ACCOUNT_NAME="${COSMOS_ARM_ID##*/databaseAccounts/}"

ROLE_DEFINITION_GUID="00000000-0000-0000-0000-000000000002"
DATA_SCOPE="/"


## Resolve ACR id/login server if ACR exists
ACR_ID=""
ACR_LOGIN_SERVER=""

if az acr show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
    ACR_ID=$(az acr show \
        --name "$ACR_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query id -o tsv)

    ACR_LOGIN_SERVER=$(az acr show \
        --name "$ACR_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query loginServer -o tsv)
else
    echo "ACR not found, skipping ACR-related cleanup: $ACR_NAME"
fi


## Resolve UAI principal id / resource id if identity exists
UAI_EXISTS=$(az identity show \
    --name "$USER_MANAGED_ID" \
    --resource-group "$RESOURCE_GROUP" \
    --query name -o tsv 2>/dev/null || true)

UAI_PRINCIPAL_ID=""
UAMI_ID=""

if [ -n "$UAI_EXISTS" ]; then
    UAI_PRINCIPAL_ID=$(az identity show \
        --name "$USER_MANAGED_ID" \
        --resource-group "$RESOURCE_GROUP" \
        --query principalId -o tsv)

    UAMI_ID=$(az identity show \
        --name "$USER_MANAGED_ID" \
        --resource-group "$RESOURCE_GROUP" \
        --query id -o tsv)
else
    echo "User managed identity not found, skipping identity-based role cleanup unless assignment can be found another way: $USER_MANAGED_ID"
fi


## 1) Delete Container App
CONTAINERAPP_EXISTS=$(az containerapp show \
    --name "$CONTAINERAPP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query name -o tsv 2>/dev/null || true)

if [ -n "$CONTAINERAPP_EXISTS" ]; then
    echo "Deleting container app: $CONTAINERAPP_NAME"

    az containerapp delete \
        --name "$CONTAINERAPP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --yes

    echo "Deleted container app: $CONTAINERAPP_NAME"
else
    echo "Container app does not exist, skipping: $CONTAINERAPP_NAME"
fi


## 2) Delete Cosmos DB SQL data-plane role assignment
if [ -n "$UAI_PRINCIPAL_ID" ]; then
    echo "Checking Cosmos DB SQL data-plane role assignments for principal: $UAI_PRINCIPAL_ID"

    COSMOS_ROLE_ASSIGNMENT_IDS=$(az cosmosdb sql role assignment list \
        --account-name "$COSMOS_ACCOUNT_NAME" \
        --resource-group "$COSMOS_RG" \
        --query "[?principalId=='$UAI_PRINCIPAL_ID' && ends_with(roleDefinitionId, '$ROLE_DEFINITION_GUID')].id" \
        -o tsv)

    if [ -n "$COSMOS_ROLE_ASSIGNMENT_IDS" ]; then
        while IFS= read -r ROLE_ASSIGNMENT_ID; do
            if [ -n "$ROLE_ASSIGNMENT_ID" ]; then
                echo "Deleting Cosmos DB SQL role assignment: $ROLE_ASSIGNMENT_ID"

                az cosmosdb sql role assignment delete \
                    --account-name "$COSMOS_ACCOUNT_NAME" \
                    --resource-group "$COSMOS_RG" \
                    --role-assignment-id "$ROLE_ASSIGNMENT_ID" \
                    --yes
            fi
        done <<< "$COSMOS_ROLE_ASSIGNMENT_IDS"

        echo "Deleted Cosmos DB SQL data-plane role assignments."
    else
        echo "No matching Cosmos DB SQL data-plane role assignment found."
    fi
else
    echo "Skipping Cosmos DB SQL role assignment cleanup because UAI principal id is unavailable."
fi


## 3) Delete Foundry User RBAC assignment
if [ -n "$UAI_PRINCIPAL_ID" ]; then
    FOUNDRY_ID=$(az cognitiveservices account show \
        --name "$FOUNDRY_RESOURCE_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query id -o tsv 2>/dev/null || true)

    if [ -n "$FOUNDRY_ID" ]; then
        FOUNDRY_ROLE_NAME="Foundry User"

        FOUND_FOUNDRY_ROLE=$(az role assignment list \
            --assignee-object-id "$UAI_PRINCIPAL_ID" \
            --role "$FOUNDRY_ROLE_NAME" \
            --scope "$FOUNDRY_ID" \
            --query "[?roleDefinitionName=='$FOUNDRY_ROLE_NAME'] | length(@)" \
            -o tsv)

        if [ "$FOUND_FOUNDRY_ROLE" -gt 0 ]; then
            echo "Deleting $FOUNDRY_ROLE_NAME role assignment from Foundry resource."

            az role assignment delete \
                --assignee-object-id "$UAI_PRINCIPAL_ID" \
                --role "$FOUNDRY_ROLE_NAME" \
                --scope "$FOUNDRY_ID"

            echo "Deleted $FOUNDRY_ROLE_NAME role assignment."
        else
            echo "No $FOUNDRY_ROLE_NAME role assignment found."
        fi
    else
        echo "Foundry resource not found, skipping Foundry role cleanup: $FOUNDRY_RESOURCE_NAME"
    fi
else
    echo "Skipping Foundry role cleanup because UAI principal id is unavailable."
fi


## 4) Delete AcrPull RBAC assignment
if [ -n "$UAI_PRINCIPAL_ID" ] && [ -n "$ACR_ID" ]; then
    FOUND_ACRPULL_ROLE=$(az role assignment list \
        --assignee-object-id "$UAI_PRINCIPAL_ID" \
        --role AcrPull \
        --scope "$ACR_ID" \
        --query "[?roleDefinitionName=='AcrPull'] | length(@)" \
        -o tsv)

    if [ "$FOUND_ACRPULL_ROLE" -gt 0 ]; then
        echo "Deleting AcrPull role assignment from ACR."

        az role assignment delete \
            --assignee-object-id "$UAI_PRINCIPAL_ID" \
            --role AcrPull \
            --scope "$ACR_ID"

        echo "Deleted AcrPull role assignment."
    else
        echo "No AcrPull role assignment found."
    fi
else
    echo "Skipping AcrPull cleanup because UAI principal id or ACR id is unavailable."
fi


## 5) Delete image/tag from ACR
if [ "$DELETE_ACR_IMAGE" = true ] && [ -n "$ACR_LOGIN_SERVER" ]; then
    echo "Checking ACR image: $LOCAL_IMAGE_NAME:$LOCAL_IMAGE_NAME_TAG"

    IMAGE_EXISTS=$(az acr repository show-tags \
        --name "$ACR_NAME" \
        --repository "$LOCAL_IMAGE_NAME" \
        --query "[?@=='$LOCAL_IMAGE_NAME_TAG'] | length(@)" \
        -o tsv 2>/dev/null || echo "0")

    if [ "$IMAGE_EXISTS" -gt 0 ]; then
        echo "Deleting ACR image: $LOCAL_IMAGE_NAME:$LOCAL_IMAGE_NAME_TAG"

        az acr repository delete \
            --name "$ACR_NAME" \
            --image "$LOCAL_IMAGE_NAME:$LOCAL_IMAGE_NAME_TAG" \
            --yes

        echo "Deleted ACR image: $LOCAL_IMAGE_NAME:$LOCAL_IMAGE_NAME_TAG"
    else
        echo "ACR image tag not found, skipping: $LOCAL_IMAGE_NAME:$LOCAL_IMAGE_NAME_TAG"
    fi
else
    echo "Skipping ACR image deletion. DELETE_ACR_IMAGE=$DELETE_ACR_IMAGE"
fi


## 6) Delete User Managed Identity - optional
if [ "$DELETE_USER_MANAGED_ID" = true ]; then
    UAI_EXISTS=$(az identity show \
        --name "$USER_MANAGED_ID" \
        --resource-group "$RESOURCE_GROUP" \
        --query name -o tsv 2>/dev/null || true)

    if [ -n "$UAI_EXISTS" ]; then
        echo "Deleting user managed identity: $USER_MANAGED_ID"

        az identity delete \
            --name "$USER_MANAGED_ID" \
            --resource-group "$RESOURCE_GROUP"

        echo "Deleted user managed identity: $USER_MANAGED_ID"
    else
        echo "User managed identity does not exist, skipping: $USER_MANAGED_ID"
    fi
else
    echo "Skipping user managed identity deletion. DELETE_USER_MANAGED_ID=false"
fi


## 7) Delete Container App Environment - optional
if [ "$DELETE_CONTAINERAPP_ENV" = true ]; then
    ENV_EXISTS=$(az containerapp env show \
        --name "$CONTAINERAPP_ENV_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query name -o tsv 2>/dev/null || true)

    if [ -n "$ENV_EXISTS" ]; then
        echo "Deleting container app environment: $CONTAINERAPP_ENV_NAME"

        az containerapp env delete \
            --name "$CONTAINERAPP_ENV_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --yes

        echo "Deleted container app environment: $CONTAINERAPP_ENV_NAME"
    else
        echo "Container app environment does not exist, skipping: $CONTAINERAPP_ENV_NAME"
    fi
else
    echo "Skipping container app environment deletion. DELETE_CONTAINERAPP_ENV=false"
fi


