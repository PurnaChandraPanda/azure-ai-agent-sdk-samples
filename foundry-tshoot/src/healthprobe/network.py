import socket
import ssl
import time
import requests
from urllib.parse import urlparse

from .models import ProbeResult


def normalize_host(value: str) -> str:
    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        return parsed.hostname or value
    return value.split("/")[0].split(":")[0]


def dns_resolve(host: str) -> ProbeResult:
    try:
        infos = socket.getaddrinfo(host, None)
        ips = sorted({info[4][0] for info in infos})
        return ProbeResult.success(
            "network",
            "dns_resolve",
            f"Resolved {host}",
            host=host,
            ips=ips,
        )
    except Exception as e:
        return ProbeResult.failure(
            "network",
            "dns_resolve",
            f"DNS resolution failed for {host}: {e}",
            host=host,
            error=str(e),
        )


def tcp_tls_probe(host: str, port: int = 443, timeout: float = 5.0) -> ProbeResult:
    try:
        start = time.time()
        sock = socket.create_connection((host, port), timeout=timeout)
        tcp_ms = (time.time() - start) * 1000

        ctx = ssl.create_default_context()
        tls_start = time.time()

        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            tls_ms = (time.time() - tls_start) * 1000
            cert = ssock.getpeercert() or {}
                        
            # read socket details - including caller and destination
            local_ip, local_port = ssock.getsockname()
            remote_ip, remote_port = ssock.getpeername()

            return ProbeResult.success(
                "network",
                "tcp_tls",
                f"TCP/TLS succeeded for {host}:{port}",
                host=host,
                port=port,

                # DNS/connection routing information
                container_local_ip=local_ip,
                container_local_port=local_port,
                remote_ip=remote_ip,
                remote_port=remote_port,

                # timing
                tcp_ms=tcp_ms,
                tls_ms=tls_ms,

                # tls details
                tls_version=ssock.version(),
                cipher=str(ssock.cipher()),
                cert_not_after=cert.get("notAfter"),
                cert_subject=str(cert.get("subject")),
                cert_issuer=str(cert.get("issuer")),
            )
    except Exception as e:
        return ProbeResult.failure(
            "network",
            "tcp_tls",
            f"TCP/TLS failed for {host}:{port}: {e}",
            host=host,
            port=port,
            error=str(e),
        )


def http_get(url: str, timeout: float = 8.0) -> ProbeResult:
    try:
        start = time.time()
        response = requests.get(url, timeout=timeout)
        elapsed_ms = (time.time() - start) * 1000

        return ProbeResult(
            service="network",
            check_name="http_get",
            ok=response.ok,
            severity="info" if response.ok else "error",
            elapsed_ms=elapsed_ms,
            message=f"HTTP GET {url} returned {response.status_code}",
            details={
                "url": url,
                "status_code": response.status_code,
                "content_type": response.headers.get("Content-Type"),
                "headers_subset": {
                    k: response.headers.get(k)
                    for k in ["Date", "Server", "x-ms-request-id"]
                    if k in response.headers
                },
                "body_preview": response.text[:500],
            },
        )
    except Exception as e:
        return ProbeResult.failure(
            "network",
            "http_get",
            f"HTTP GET failed for {url}: {e}",
            url=url,
        )