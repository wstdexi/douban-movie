from contextvars import ContextVar

CTX_X_REQUEST_ID: ContextVar[str] = ContextVar("x_request_id", default="-")
