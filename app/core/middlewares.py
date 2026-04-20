import time
import uuid

from fastapi import FastAPI, Request

from app.core.ctx import CTX_X_REQUEST_ID
from app.log.log import log


def register_middlewares(app: FastAPI) -> None:
    """Register HTTP middlewares for the FastAPI app."""
    @app.middleware("http")
    async def request_log_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        token = CTX_X_REQUEST_ID.set(request_id)
        start = time.perf_counter()
        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start) * 1000
            response.headers["X-Request-ID"] = request_id
            log.bind(x_request_id=request_id).info(
                "{} {} -> {} | {:.2f}ms | client={}",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
                request.client.host if request.client else "unknown",
            )
            return response
        finally:
            CTX_X_REQUEST_ID.reset(token)

