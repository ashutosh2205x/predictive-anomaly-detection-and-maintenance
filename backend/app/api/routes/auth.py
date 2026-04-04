from __future__ import annotations

import hmac

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR

from app.auth.jwt_tokens import AuthConfigError, create_access_token
from app.auth.settings import ALLOWED_EMAILS, AUTH_PASSWORD

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    email = (body.email or "").strip().lower()
    password = body.password or ""


    if not ALLOWED_EMAILS or not AUTH_PASSWORD:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth not configured on server",
        )

    if not email or "@" not in email:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if email not in ALLOWED_EMAILS:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not hmac.compare_digest(password, AUTH_PASSWORD):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    try:
        token = create_access_token(email=email)
    except AuthConfigError:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth not configured on server",
            error = AuthConfigError
        )

    return TokenResponse(access_token=token)
