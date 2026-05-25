from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import time


@dataclass
class ProbeResult:
    service: str
    check_name: str
    ok: bool
    severity: str = "info"  # info | warning | error
    elapsed_ms: Optional[float] = None
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def success(service: str, check_name: str, message: str = "", **details):
        return ProbeResult(
            service=service,
            check_name=check_name,
            ok=True,
            severity="info",
            message=message,
            details=details,
        )

    @staticmethod
    def failure(service: str, check_name: str, message: str, **details):
        return ProbeResult(
            service=service,
            check_name=check_name,
            ok=False,
            severity="error",
            message=message,
            details=details,
        )


def timed_call(fn, *args, **kwargs):
    start = time.time()
    try:
        value = fn(*args, **kwargs)
        elapsed_ms = (time.time() - start) * 1000
        return value, elapsed_ms, None
    except Exception as e:
        elapsed_ms = (time.time() - start) * 1000
        return None, elapsed_ms, e