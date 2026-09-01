import hashlib
import hmac
import time
from typing import Optional
from fastapi import APIRouter, Cookie, Header, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str


def generate_session_token(username: str) -> str:
    """Generate a tamper-proof session token."""
    timestamp = str(int(time.time()))
    payload = f"{username}:{timestamp}"
    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return f"{payload}:{signature}"


def verify_session_token(token: Optional[str]) -> bool:
    """Validate token signature and expiration (7 days)."""
    if not token or ":" not in token:
        return False
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return False
        username, timestamp_str, sig = parts
        timestamp = int(timestamp_str)

        # Check expiration (7 days)
        if time.time() - timestamp > (7 * 24 * 3600):
            return False

        expected = hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            f"{username}:{timestamp_str}".encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(sig, expected)
    except Exception:
        return False


@router.post("/login")
async def login(payload: LoginRequest, response: Response):
    """
    Authenticate administrator credentials.
    """
    user_clean = payload.username.strip()
    pass_clean = payload.password.strip()

    if user_clean == settings.ADMIN_USERNAME and pass_clean == settings.ADMIN_PASSWORD:
        token = generate_session_token(user_clean)
        
        # Set HTTP-only Cookie
        response.set_cookie(
            key="stellar_admin_session",
            value=token,
            httponly=True,
            max_age=7 * 24 * 3600,
            samesite="lax"
        )

        return {
            "success": True,
            "message": "Login successful",
            "token": token,
            "user": {
                "username": user_clean,
                "role": "Administrator"
            }
        }

    raise HTTPException(status_code=401, detail="Invalid username or password.")


@router.post("/logout")
async def logout(response: Response):
    """
    Sign out administrator and clear session cookie.
    """
    response.delete_cookie("stellar_admin_session")
    return {"success": True, "message": "Logged out successfully"}


@router.get("/me")
async def get_current_user(
    stellar_admin_session: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    """
    Verify current active authentication session.
    """
    token = stellar_admin_session
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ")[1].strip()

    if verify_session_token(token):
        return {
            "authenticated": True,
            "user": {
                "username": settings.ADMIN_USERNAME,
                "role": "Administrator"
            }
        }

    return JSONResponse(status_code=401, content={"authenticated": False, "message": "Not authenticated"})
