from contextvars import ContextVar

# Per-request id for log correlation.
CTX_X_REQUEST_ID: ContextVar[str] = ContextVar("x_request_id", default="-")
