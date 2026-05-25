# tests/test_cosmos_live.py


import os
import pytest

from azure.cosmos import CosmosClient
from healthprobe.plugins.cosmos import CosmosPlugin

RUN_LIVE_COSMOS_TESTS = os.getenv("RUN_LIVE_COSMOS_TESTS")

@pytest.mark.skipif(
    not RUN_LIVE_COSMOS_TESTS,
    reason="Live Cosmos tests disabled. Set RUN_LIVE_COSMOS_TESTS=1 to enable.",
)
def test_live_cosmos_plugin_account_metadata_only():
    endpoint = require_env("COSMOS_ENDPOINT")

    plugin = CosmosPlugin()

    config = {
        "endpoint": endpoint,
        "database": database,
        "container": container,
        "timeout": float(os.getenv("COSMOS_TIMEOUT", "8")),
        "probe_mode": "Account metadata + container metadata",
    }

    results = plugin.run(config)

    summary = {
        r.check_name: {
            "ok": r.ok,
            "message": r.message,
            "details": r.details,
        }
        for r in results
    }

    dns_result = find_result(results, "dns_resolve")
    tls_result = find_result(results, "tcp_tls")
    account_result = find_result(results, "account_metadata")
    database_result = find_result(results, "read_database")
    container_result = find_result(results, "read_container")

    assert dns_result.ok is True, summary
    assert tls_result.ok is True, summary
    assert account_result.ok is True, summary
    assert database_result.ok is True, summary
    assert container_result.ok is True, summary

    assert database_result.details["database"] == database
    assert container_result.details["database"] == database
    assert container_result.details["container"] == container
    assert container_result.details["container_id"] == container
    assert "partition_key" in container_result.details


@pytest.mark.skipif(
    not RUN_LIVE_COSMOS_TESTS,
    reason="Live Cosmos tests disabled. Set RUN_LIVE_COSMOS_TESTS=1 to enable.",
)
def test_live_cosmos_sdk_account_metadata_direct():
    endpoint = require_env("COSMOS_ENDPOINT")

    credential = get_credential()
    client = CosmosClient(endpoint, credential=credential)

    try:
        account = client.get_database_account()
    except CosmosHttpResponseError as e:
        pytest.fail(
            f"Cosmos account metadata read failed. "
            f"Status={e.status_code}, Error={str(e)}"
        )

    assert account is not None
    assert hasattr(account, "DatabasesLink")
    assert hasattr(account, "ConsistencyPolicy")


@pytest.mark.skipif(
    not RUN_LIVE_COSMOS_TESTS,
    reason="Live Cosmos tests disabled. Set RUN_LIVE_COSMOS_TESTS=1 to enable.",
)
def test_live_cosmos_sdk_container_metadata_direct():
    endpoint = require_env("COSMOS_ENDPOINT")
    database = require_env("COSMOS_DATABASE")
    container = require_env("COSMOS_CONTAINER")

    credential = get_credential()
    client = CosmosClient(endpoint, credential=credential)

    container_client = (
        client
        .get_database_client(database)
        .get_container_client(container)
    )

    try:
        props = container_client.read()
    except CosmosHttpResponseError as e:
        pytest.fail(
            f"Cosmos container metadata read failed. "
            f"Database={database}, Container={container}, "
            f"Status={e.status_code}, Error={str(e)}"
        )

    assert props is not None
    assert props["id"] == container
    assert "partitionKey" in props


@pytest.mark.skipif(
    not RUN_LIVE_COSMOS_TESTS,
    reason="Live Cosmos tests disabled. Set RUN_LIVE_COSMOS_TESTS=1 to enable.",
)
def test_live_cosmos_sdk_point_read_if_configured():
    endpoint = require_env("COSMOS_ENDPOINT")
    database = require_env("COSMOS_DATABASE")
    container = require_env("COSMOS_CONTAINER")

    item_id = os.getenv("COSMOS_HEALTH_ITEM_ID")
    partition_key = os.getenv("COSMOS_HEALTH_PARTITION_KEY")

    if not item_id or not partition_key:
        pytest.skip(
            "COSMOS_HEALTH_ITEM_ID and COSMOS_HEALTH_PARTITION_KEY are not set. "
            "Skipping point-read test."
        )

    credential = get_credential()
    client = CosmosClient(endpoint, credential=credential)

    container_client = (
        client
        .get_database_client(database)
        .get_container_client(container)
    )

    try:
        doc = container_client.read_item(
            item=item_id,
            partition_key=partition_key,
        )
    except CosmosHttpResponseError as e:
        pytest.fail(
            f"Cosmos point-read failed. "
            f"Database={database}, Container={container}, "
            f"Item={item_id}, PartitionKey={partition_key}, "
            f"Status={e.status_code}, Error={str(e)}"
        )

    assert doc["id"] == item_id
from azure.cosmos.exceptions import CosmosHttpResponseError

from healthprobe.auth import get_credential
from healthprobe.plugins.cosmos import CosmosPlugin


RUN_LIVE_COSMOS_TESTS = os.getenv("RUN_LIVE_COSMOS_TESTS", "0") == "1"


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        pytest.skip(f"{name} is not set")
    return value


def find_result(results, check_name: str):
    for result in results:
        if result.check_name == check_name:
            return result

    available = [r.check_name for r in results]
    raise AssertionError(f"Check '{check_name}' not found. Available checks: {available}")


@pytest.mark.skipif(
    not RUN_LIVE_COSMOS_TESTS,
    reason="Live Cosmos tests disabled. Set RUN_LIVE_COSMOS_TESTS=1 to enable.",
)
def test_live_cosmos_plugin_account_metadata_only():
    endpoint = require_env("COSMOS_ENDPOINT")

    plugin = CosmosPlugin()

    config = {
        "endpoint": endpoint,
        "database": os.getenv("COSMOS_DATABASE", ""),
        "container": os.getenv("COSMOS_CONTAINER", ""),
        "timeout": float(os.getenv("COSMOS_TIMEOUT", "8")),
        "probe_mode": "Account metadata only",
    }

    results = plugin.run(config)

    summary = {
        r.check_name: {
            "ok": r.ok,
            "message": r.message,
            "details": r.details,
        }
        for r in results
    }

    dns_result = find_result(results, "dns_resolve")
    tls_result = find_result(results, "tcp_tls")
    account_result = find_result(results, "account_metadata")

    assert dns_result.ok is True, summary
    assert tls_result.ok is True, summary
    assert account_result.ok is True, summary

    assert account_result.details.get("databases_link") is not None
    assert "consistency_policy" in account_result.details


@pytest.mark.skipif(
    not RUN_LIVE_COSMOS_TESTS,
    reason="Live Cosmos tests disabled. Set RUN_LIVE_COSMOS_TESTS=1 to enable.",
)
def test_live_cosmos_plugin_container_metadata_read():
    endpoint = require_env("COSMOS_ENDPOINT")
    database = require_env("COSMOS_DATABASE")
    container = require_env("COSMOS_CONTAINER")

