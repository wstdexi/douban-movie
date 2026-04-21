import time
import uuid

from fastapi import HTTPException
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.deps import resolve_current_user_from_token
from app.core.ctx import CTX_X_REQUEST_ID
from app.models.system.session import SessionLocal
from app.log.log import log


def register_middlewares(app: FastAPI) -> None:
    """Register HTTP middlewares for the FastAPI app."""
    public_paths = {
        "/",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/v1/auth/login",
        "/v1/auth/register",
        "/v1/auth/refresh",
    }

    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        path = request.url.path
        if path in public_paths:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.lower().startswith("bearer "):
            log.bind(x_request_id=CTX_X_REQUEST_ID.get()).warning(
                "Auth failed: missing bearer token | path={}",
                path,
            )
            return JSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            log.bind(x_request_id=CTX_X_REQUEST_ID.get()).warning(
                "Auth failed: empty bearer token | path={}",
                path,
            )
            return JSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        with SessionLocal() as db:
            try:
                request.state.current_user = resolve_current_user_from_token(token, db)
            except HTTPException as exc:
                log.bind(x_request_id=CTX_X_REQUEST_ID.get()).warning(
                    "Auth failed: {} | path={}",
                    exc.detail,
                    path,
                )
                return JSONResponse(
                    status_code=exc.status_code,
                    content={"detail": exc.detail},
                    headers=exc.headers or {},
                )
        log.bind(x_request_id=CTX_X_REQUEST_ID.get()).info(
            "Auth passed: user_id={} | path={}",
            request.state.current_user.id,
            path,
        )
        return await call_next(request)

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

