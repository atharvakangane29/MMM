# backend/routers/auth.py
"""
Authentication router.
Credentials are stored server-side in APP_USERS env var — never hardcoded.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from jose import JWTError, jwt

from config import Settings, get_settings
from schemas.auth import LoginRequest, LoginResponse, MeResponse, UserInfo

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=False)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_token(settings: Settings, email: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expire_hours)
    payload = {"sub": email, "role": role, "exp": expire}
    return jwt.encode(payload, settings.api_secret_key, algorithm=settings.jwt_algorithm)


def _find_user(settings: Settings, email: str, password: str) -> dict | None:
    for u in settings.user_credentials:
        if u["email"].lower() == email.lower() and u["password"] == password:
            return u
    return None


def _decode_token(settings: Settings, token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.api_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc


# ─────────────────────────────────────────────────────────────────────────────
# Dependency: get current user from Bearer token
# ─────────────────────────────────────────────────────────────────────────────

def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = _decode_token(settings, credentials.credentials)
    return payload


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, settings: Annotated[Settings, Depends(get_settings)]):
    user = _find_user(settings, body.email, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    token = _make_token(settings, user["email"], user["role"])
    # Derive display name from email (first part before @)
    name = user["email"].split("@")[0].replace(".", " ").title()
    return LoginResponse(
        access_token=token,
        expires_in=settings.jwt_expire_hours * 3600,
        user=UserInfo(name=name, email=user["email"], role=user["role"]),
    )


@router.post("/logout")
def logout():
    # JWT is stateless — client must discard the token
    return {"message": "Logged out successfully."}


@router.get("/me", response_model=MeResponse)
def me(current_user: Annotated[dict, Depends(get_current_user)]):
    email = current_user.get("sub", "")
    role = current_user.get("role", "analyst")
    name = email.split("@")[0].replace(".", " ").title()
    return MeResponse(user=UserInfo(name=name, email=email, role=role))
