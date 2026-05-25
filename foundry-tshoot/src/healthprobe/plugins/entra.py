import streamlit as st

from healthprobe.network import dns_resolve, tcp_tls_probe, http_get
from healthprobe.models import ProbeResult


class EntraPlugin:
    name = "Entra ID"

    def render_config(self):
        st.caption("Checks login.microsoftonline.com DNS, TLS, and OIDC metadata endpoint.")

        return {
            "host": st.text_input(
                "Authority host",
                "login.microsoftonline.com",
                key="entra_host",
            ),
            "oidc_url": st.text_input(
                "OIDC discovery URL",
                "https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration",
                key="entra_oidc",
            ),
            "timeout": st.number_input(
                "Timeout seconds",
                1.0,
                30.0,
                8.0,
                key="entra_timeout",
            ),
        }

    def run(self, config):
        host = config["host"]
        return [
            dns_resolve(host),
            tcp_tls_probe(host, 443, config["timeout"]),
            http_get(config["oidc_url"], config["timeout"]),
        ]