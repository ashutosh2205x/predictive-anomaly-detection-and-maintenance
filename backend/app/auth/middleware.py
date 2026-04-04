from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED

from app.auth.jwt_tokens import AuthConfigError, decode_access_token
from app.auth.settings import ALLOWED_EMAILS


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, public_paths: set[str] | None = None):
        super().__init__(app)
        self._public_paths = public_paths or set()

    def _is_public_path(self, path: str) -> bool:
        if path in self._public_paths:
            return True

        # FastAPI docs and related endpoints.
        if path.startswith("/docs"):
            return True
        if path.startswith("/redoc"):
            return True
        if path == "/openapi.json":
            return True

        return False

    async def dispatch(self, request: Request, call_next):
        if self._is_public_path(request.url.path):
            return await call_next(request)

        auth = request.headers.get("authorization") or ""
        if not auth.lower().startswith("bearer "):
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid Authorization header"},
            )

        token = auth.split(" ", 1)[1].strip()
        if not token:
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing bearer token"},
            )

        try:
            payload = decode_access_token(token)
        except AuthConfigError:
            # Auth is enabled but not configured correctly on the server.
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"detail": "Authorization is not configured"},
            )
        except Exception:
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
            )

        email = (payload.get("email") or payload.get("sub") or "").strip().lower()
        if not email:
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"detail": "Token missing email"},
            )

        # If no allowlist is configured, reject everything by default.
        if not ALLOWED_EMAILS or email not in ALLOWED_EMAILS:
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authorized"},
            )

        request.state.email = email
        return await call_next(request)

