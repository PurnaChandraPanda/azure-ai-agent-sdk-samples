# tests/test_network.py

import pytest

from healthprobe.network import (
    normalize_host,
    dns_resolve,
    tcp_tls_probe,
    http_get,
)


# -----------------------------
# normalize_host tests
# -----------------------------

@pytest.mark.parametrize(
    "input_value, expected",
    [
        ("https://abc.documents.azure.com:443/", "abc.documents.azure.com"),
        ("http://example.com/path", "example.com"),
        ("login.microsoftonline.com", "login.microsoftonline.com"),
        ("abc.documents.azure.com:443", "abc.documents.azure.com"),
        ("abc.documents.azure.com/some/path", "abc.documents.azure.com"),
        ("https://myaccount.blob.core.windows.net/container/blob.txt", "myaccount.blob.core.windows.net"),
        ("https://mysearch.search.windows.net/indexes/myindex", "mysearch.search.windows.net"),
    ],
)
def test_normalize_host(input_value, expected):
    assert normalize_host(input_value) == expected

def test_dns_resolve_success():
    
    result = dns_resolve("login.microsoftonline.com")

    assert result.ok is True
    assert result.service == "network"
    assert result.check_name == "dns_resolve"
    assert result.details["host"] == "login.microsoftonline.com"
    assert len(result.details["ips"]) > 0

# ----------------------
# Live online tests
# ----------------------

def test_live_entra_dns_tls_http():
    host = "login.microsoftonline.com"

    dns_result = dns_resolve(host)
    assert dns_result.ok is True
    assert len(dns_result.details["ips"]) > 0

    tls_result = tcp_tls_probe(host, 443, timeout=8)
    assert tls_result.ok is True
    assert tls_result.details["tls_version"] is not None

    http_result = http_get(
        "https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration",
        timeout=8,
    )
    assert http_result.ok is True
    assert http_result.details["status_code"] == 200
