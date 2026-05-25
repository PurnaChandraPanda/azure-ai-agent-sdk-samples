import os
from azure.identity import DefaultAzureCredential, AzureCliCredential


def get_credential():
    """
    Uses:
    - Local laptop: Azure CLI / Azure PowerShell / VS Code auth etc.
    - Azure Container Apps: Managed Identity
    """
    managed_identity_client_id = os.getenv("AZURE_CONTAINERAPP_CLIENT_ID")

    if managed_identity_client_id:
        return DefaultAzureCredential(
            managed_identity_client_id=managed_identity_client_id
        )
    
    return DefaultAzureCredential()