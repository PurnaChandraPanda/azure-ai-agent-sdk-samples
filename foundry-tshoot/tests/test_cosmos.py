
import pytest
from azure.identity import DefaultAzureCredential,AzureCliCredential
from azure.cosmos import CosmosClient

endpoint = "https://aifoundry3738cosmosdb.documents.azure.com:443/"

def test_auth():
    # credential = DefaultAzureCredential()
    credential = AzureCliCredential()
    client = CosmosClient(endpoint, credential=credential)
    
    print("ok")

test_auth()
