import streamlit as st

from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

from healthprobe.auth import get_credential
from healthprobe.network import dns_resolve, tcp_tls_probe, normalize_host
from healthprobe.models import ProbeResult, timed_call



class CosmosPlugin:
    name = "Azure Cosmos DB for NoSQL"

    def render_config(self):
        st.caption(
            "Checks Cosmos endpoint DNS/TLS and performs Cosmos data-plane checks "
            "using Managed Identity / Entra ID."
        )

        probe_mode = st.selectbox(
            "Cosmos probe mode",
            [
                "Account metadata only",
                "Read database/container metadata",
                "Point-read known item",
                "Query TOP 1 item",
            ],
            key="cosmos_probe_mode",
        )

        return {
            "endpoint": st.text_input(
                "Cosmos endpoint",
                "https://<account>.documents.azure.com:443/",
                key="cosmos_endpoint",
            ),
            "database": st.text_input("Database", "appdb", key="cosmos_db"),
            "container": st.text_input("Container", "health", key="cosmos_container"),
            "item_id": st.text_input(
                "Item id",
                "ent_msg_cihhz8056NjehVydyT6FqBEj",
                key="cosmos_item_id",
            ),
            "partition_key": st.text_input(
                "Partition key value",
                "2f48551e-5805-4ed7-b0b6-aa98c259fda9_2026_03",
                key="cosmos_pk",
            ),
            "probe_mode": probe_mode,
            "timeout": st.number_input(
                "Timeout seconds",
                1.0,
                30.0,
                8.0,
                key="cosmos_timeout",
            ),
        }

    
    def _client(self, endpoint):
        credential = get_credential()
        return CosmosClient(endpoint, credential=credential)

    def _error_result(self, check_name, error):
        if isinstance(error, CosmosHttpResponseError):
            return ProbeResult.failure(
                self.name,
                check_name,
                f"Cosmos {check_name} failed: {error.status_code}",
                status_code=error.status_code,
                error=str(error),
            )

        return ProbeResult.failure(
            self.name,
            check_name,
            f"Cosmos {check_name} failed: {error}",
            error=str(error),
        )


    def run(self, config):
        endpoint = config["endpoint"]
        host = normalize_host(endpoint)

        results = [
            dns_resolve(host),
            tcp_tls_probe(host, 443, config["timeout"]),
        ]

        
        # 1. Account metadata probe
        def account_metadata():
            client = self._client(endpoint)
            return client.get_database_account()

        
        account, elapsed_ms, error = timed_call(account_metadata)

        if error:
            results.append(self._error_result("account_metadata", error))
            return results

        
        results.append(
            ProbeResult(
                service=self.name,
                check_name="account_metadata",
                ok=True,
                elapsed_ms=elapsed_ms,
                message="Cosmos account metadata probe succeeded",
                details={
                    "databases_link": account.DatabasesLink,
                    "readable_locations": account._ReadableLocations,
                    "writable_locations": account._WritableLocations,
                    "consistency_policy": account.ConsistencyPolicy,
                },
            )
        )        
        
        if config["probe_mode"] == "Account metadata only":
            return results

        
        # 2. Database metadata probe
        def read_database():
            client = self._client(endpoint)
            db_client = client.get_database_client(config["database"])
            return db_client.read()

        
        db_props, elapsed_ms, error = timed_call(read_database)

        if error:
            results.append(self._error_result("read_database", error))
            return results

        results.append(
            ProbeResult(
                service=self.name,
                check_name="read_database",
                ok=True,
                elapsed_ms=elapsed_ms,
                message="Cosmos database metadata read succeeded",
                details={
                    "database": db_props.get("id"),
                    "_rid": db_props.get("_rid"),
                    "_ts": db_props.get("_ts"),
                },
            )
        )

        
        # 3. Container metadata probe
        def read_container():
            client = self._client(endpoint)
            container_client = (
                client
                .get_database_client(config["database"])
                .get_container_client(config["container"])
            )
            return container_client.read()

        container_props, elapsed_ms, error = timed_call(read_container)

        if error:
            results.append(self._error_result("read_container", error))
            return results

        partition_key_info = container_props.get("partitionKey", {})

        results.append(
            ProbeResult(                
                service=self.name,
                check_name="read_container",
                ok=True,
                elapsed_ms=elapsed_ms,
                message="Cosmos container metadata read succeeded",                
                details={
                        "endpoint": endpoint,
                        "database": config["database"],
                        "container": config["container"],
                        "container_id": container_props.get("id"),
                        "partition_key": container_props.get("partitionKey"),
                        "indexing_policy": container_props.get("indexingPolicy"),
                        "default_ttl": container_props.get("defaultTtl"),
                    },
            )
        )

        return results