from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        if request.url.path.startswith("/api"):
            token = request.headers.get("Authorization", "")
            expected = f"Bearer {settings.app_token}"
            if token != expected:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "detail": "Unauthorized"},
                )

        return await call_next(request)
