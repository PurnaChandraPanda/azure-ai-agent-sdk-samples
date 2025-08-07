import time, logging
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logging.basicConfig(level=logging.INFO, 
                    format="%(levelname)s - %(message)s")
_logger = logging.getLogger("uvicorn.error")    # <- prints to console with no extras

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = (time.perf_counter() - start) * 1000
        _logger.info("timing: %s %s -> %s %.2f ms",
                 request.method, request.url.path, response.status_code, elapsed)

        response.headers["X-Process-Time"] = f"{elapsed:.2f}ms"
        return response