# tests/test_cosmos_plugin.py

from unittest.mock import Mock, patch

from azure.cosmos.exceptions import CosmosHttpResponseError


def mock_probe_success(check_name):
    return ProbeResult.success(
        service="network",
        check_name=check_name,
        message=f"{check_name} succeeded",
    )


class FakeDatabaseAccount:
    def __init__(self):
        self.DatabasesLink = "/dbs/"
        self.MediaLink = "/media/"
        self.MaxMediaStorageUsageInMB = 0
        self.CurrentMediaStorageUsageInMB = 0
        self.ConsumedDocumentStorageInMB = 0
        self.ReservedDocumentStorageInMB = 0
        self.ProvisionedDocumentStorageInMB = 0
        self.ConsistencyPolicy = {
            "defaultConsistencyLevel": "Session"
        }
        self._WritableLocations = [
            {
                "name": "East US",
                "databaseAccountEndpoint": "https://mycosmos-eastus.documents.azure.com:443/"
            }
        ]
        self._ReadableLocations = [
            {
                "name": "East US",
                "databaseAccountEndpoint": "https://mycosmos-eastus.documents.azure.com:443/"
            }
        ]
        self._EnableMultipleWritableLocations = False
        self._EnablePerPartitionFailoverBehavior = False

from healthprobe.models import ProbeResult
from healthprobe.plugins.cosmos import CosmosPlugin


def sample_config(
    probe_mode="Account metadata + container metadata",
):
    return {
        "endpoint": "https://mycosmos.documents.azure.com:443/",
        "database": "appdb",
        "container": "health",
        "timeout": 8,
        "probe_mode": probe_mode,
    }

@patch("healthprobe.plugins.cosmos.tcp_tls_probe")
@patch("healthprobe.plugins.cosmos.dns_resolve")
@patch("healthprobe.plugins.cosmos.get_credential")
@patch("healthprobe.plugins.cosmos.CosmosClient")
def test_cosmos_account_metadata_success(
    mock_cosmos_client,
    mock_get_credential,
    mock_dns_resolve,
    mock_tcp_tls_probe,
):
    mock_dns_resolve.return_value = mock_probe_success("dns_resolve")
    mock_tcp_tls_probe.return_value = mock_probe_success("tcp_tls")
    mock_get_credential.return_value = Mock()

    fake_account = FakeDatabaseAccount()

    mock_client_instance = Mock()
    mock_client_instance.get_database_account.return_value = fake_account

    # If your plugin also calls read_container(), mock that path too
    mock_container_client = Mock()
    mock_container_client.read.return_value = {
        "id": "health",
        "partitionKey": {
            "paths": ["/pk"],
            "kind": "Hash",
        },
        "indexingPolicy": {
            "indexingMode": "consistent",
            "automatic": True,
        },
    }

    mock_db_client = Mock()
    mock_db_client.get_container_client.return_value = mock_container_client
    mock_client_instance.get_database_client.return_value = mock_db_client

    mock_cosmos_client.return_value = mock_client_instance

    plugin = CosmosPlugin()
    results = plugin.run(sample_config())

    account_result = next(
        result for result in results
        if result.check_name == "account_metadata"
    )

    assert account_result.ok is True
    assert account_result.service == plugin.name
    assert account_result.message == "Cosmos account metadata probe succeeded"

    assert account_result.details["databases_link"] == "/dbs/"
    # assert account_result.details["media_link"] == "/media/"
    assert account_result.details["consistency_policy"]["defaultConsistencyLevel"] == "Session"

    assert len(account_result.details["readable_locations"]) == 1
    assert account_result.details["readable_locations"][0]["name"] == "East US"

    assert len(account_result.details["writable_locations"]) == 1
    assert account_result.details["writable_locations"][0]["name"] == "East US"

    # assert account_result.details["enable_multiple_writable_locations"] is False

    mock_client_instance.get_database_account.assert_called_once()

@patch("healthprobe.plugins.cosmos.tcp_tls_probe")
@patch("healthprobe.plugins.cosmos.dns_resolve")
@patch("healthprobe.plugins.cosmos.get_credential")
@patch("healthprobe.plugins.cosmos.CosmosClient")
def test_cosmos_read_container_success(
    mock_cosmos_client,
    mock_get_credential,
    mock_dns_resolve,
    mock_tcp_tls_probe,
):
    mock_dns_resolve.return_value = mock_probe_success("dns_resolve")
    mock_tcp_tls_probe.return_value = mock_probe_success("tcp_tls")
    mock_get_credential.return_value = Mock()

    mock_client_instance = Mock()
    mock_client_instance.get_database_account.return_value = FakeDatabaseAccount()

    mock_container_client = Mock()
    mock_container_client.read.return_value = {
        "id": "health",
        "partitionKey": {
            "paths": ["/pk"],
            "kind": "Hash",
        },
        "indexingPolicy": {
            "indexingMode": "consistent",
            "automatic": True,
        },
        "defaultTtl": None,
    }

    mock_db_client = Mock()
    mock_db_client.get_container_client.return_value = mock_container_client
    mock_client_instance.get_database_client.return_value = mock_db_client

    mock_cosmos_client.return_value = mock_client_instance

    plugin = CosmosPlugin()
    results = plugin.run(sample_config())

    container_result = next(
        result for result in results
        if result.check_name == "read_container"
    )

    assert container_result.ok is True
    assert container_result.message == "Cosmos container metadata read succeeded"
    assert container_result.details["database"] == "appdb"
    assert container_result.details["container"] == "health"
    assert container_result.details["container_id"] == "health"
    assert container_result.details["partition_key"]["paths"] == ["/pk"]
        
    mock_client_instance.get_database_client.assert_any_call("appdb")
    assert mock_client_instance.get_database_client.call_count >= 1
    mock_db_client.get_container_client.assert_called_once_with("health")
    mock_container_client.read.assert_called_once()

@patch("healthprobe.plugins.cosmos.tcp_tls_probe")
@patch("healthprobe.plugins.cosmos.dns_resolve")
@patch("healthprobe.plugins.cosmos.get_credential")
@patch("healthprobe.plugins.cosmos.CosmosClient")
def test_cosmos_account_metadata_403_failure(
    mock_cosmos_client,
    mock_get_credential,
    mock_dns_resolve,
    mock_tcp_tls_probe,
):
    mock_dns_resolve.return_value = mock_probe_success("dns_resolve")
    mock_tcp_tls_probe.return_value = mock_probe_success("tcp_tls")
    mock_get_credential.return_value = Mock()

    error = CosmosHttpResponseError(
        status_code=403,
        message="Forbidden: missing Cosmos DB data-plane RBAC permission",
    )

    mock_client_instance = Mock()
    mock_client_instance.get_database_account.side_effect = error
    mock_cosmos_client.return_value = mock_client_instance

    plugin = CosmosPlugin()
    results = plugin.run(sample_config())

    account_result = next(
        result for result in results
        if result.check_name == "account_metadata"
    )

    assert account_result.ok is False
    assert account_result.severity == "error"
    assert account_result.details["status_code"] == 403
    assert "Cosmos account_metadata failed" in account_result.message

@patch("healthprobe.plugins.cosmos.tcp_tls_probe")
@patch("healthprobe.plugins.cosmos.dns_resolve")
@patch("healthprobe.plugins.cosmos.get_credential")
@patch("healthprobe.plugins.cosmos.CosmosClient")
def test_cosmos_read_container_404_failure(
    mock_cosmos_client,
    mock_get_credential,
    mock_dns_resolve,
    mock_tcp_tls_probe,
):
    mock_dns_resolve.return_value = mock_probe_success("dns_resolve")
    mock_tcp_tls_probe.return_value = mock_probe_success("tcp_tls")
    mock_get_credential.return_value = Mock()

    mock_client_instance = Mock()
    mock_client_instance.get_database_account.return_value = FakeDatabaseAccount()

    error = CosmosHttpResponseError(
        status_code=404,
        message='Message: {"Errors":["Owner resource does not exist"]}',
    )

    mock_container_client = Mock()
    mock_container_client.read.side_effect = error

    mock_db_client = Mock()
    mock_db_client.get_container_client.return_value = mock_container_client
    mock_client_instance.get_database_client.return_value = mock_db_client

    mock_cosmos_client.return_value = mock_client_instance

    plugin = CosmosPlugin()
    results = plugin.run(sample_config())

    container_result = next(
        result for result in results
        if result.check_name == "read_container"
    )

    assert container_result.ok is False
    assert container_result.severity == "error"
    assert container_result.details["status_code"] == 404
    assert "Cosmos read_container failed" in container_result.message
    assert "Owner resource does not exist" in container_result.details["error"]

@patch("healthprobe.plugins.cosmos.tcp_tls_probe")
@patch("healthprobe.plugins.cosmos.dns_resolve")
@patch("healthprobe.plugins.cosmos.get_credential")
@patch("healthprobe.plugins.cosmos.CosmosClient")
def test_cosmos_plugin_continues_when_tls_probe_fails(
    mock_cosmos_client,
    mock_get_credential,
    mock_dns_resolve,
    mock_tcp_tls_probe,
):
    mock_dns_resolve.return_value = mock_probe_success("dns_resolve")
    mock_tcp_tls_probe.return_value = ProbeResult.failure(
        service="network",
        check_name="tcp_tls",
        message="TCP/TLS failed",
    )

    mock_get_credential.return_value = Mock()

    mock_client_instance = Mock()
    mock_client_instance.get_database_account.return_value = FakeDatabaseAccount()

    mock_container_client = Mock()
    mock_container_client.read.return_value = {
        "id": "health",
        "partitionKey": {"paths": ["/pk"], "kind": "Hash"},
    }

    mock_db_client = Mock()
    mock_db_client.get_container_client.return_value = mock_container_client
    mock_client_instance.get_database_client.return_value = mock_db_client

    mock_cosmos_client.return_value = mock_client_instance

    plugin = CosmosPlugin()
    results = plugin.run(sample_config())

    tls_result = next(result for result in results if result.check_name == "tcp_tls")
    account_result = next(result for result in results if result.check_name == "account_metadata")

    assert tls_result.ok is False
    assert account_result.ok is True


