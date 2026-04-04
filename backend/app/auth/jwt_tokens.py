from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt

from app.auth.settings import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET_KEY


class AuthConfigError(RuntimeError):
    pass


def _require_secret() -> str:
    if not JWT_SECRET_KEY:
        raise AuthConfigError("JWT_SECRET_KEY is not set")
    return JWT_SECRET_KEY


def create_access_token(*, email: str) -> str:
    secret = _require_secret()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": email,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXPIRE_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    secret = _require_secret()
    return jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])

