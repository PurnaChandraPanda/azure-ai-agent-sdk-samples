# tests/test_models.py

from healthprobe.models import ProbeResult


def test_probe_result_success_factory():
    result = ProbeResult.success(
        service="network",
        check_name="dns",
        message="DNS resolved",
        host="example.com",
        ips=["93.184.216.34"],
    )

    assert result.ok is True
    assert result.service == "network"
    assert result.check_name == "dns"
    assert result.message == "DNS resolved"
    assert result.details["host"] == "example.com"
    assert result.details["ips"] == ["93.184.216.34"]


def test_probe_result_failure_factory():
    result = ProbeResult.failure(
        service="network",
        check_name="tcp_tls",
        message="Connection failed",
        host="example.com",
    )

    assert result.ok is False
    assert result.severity == "error"
    assert result.message == "Connection failed"
    assert result.details["host"] == "example.com"