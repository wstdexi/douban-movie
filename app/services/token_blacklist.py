import time

# In-memory revoked token cache. This is process-local and resets on restart.
_REVOKED_TOKENS: dict[str, int] = {}


def revoke_token(token: str, exp_timestamp: int) -> None:
    _REVOKED_TOKENS[token] = exp_timestamp


def is_token_revoked(token: str) -> bool:
    now = int(time.time())
    expired_tokens = [t for t, exp in _REVOKED_TOKENS.items() if exp <= now]
    for t in expired_tokens:
        _REVOKED_TOKENS.pop(t, None)
    return token in _REVOKED_TOKENS
