from datetime import datetime, timedelta, timezone
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_hex

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import RevokedToken, User
from .permissions import action_for_request, explicit_permission, module_for_request

bearer = HTTPBearer(auto_error=False)


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or token_hex(16)
    digest = pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 210_000).hex()
    return f"pbkdf2_sha256${salt}${digest}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        _, salt, digest = encoded.split("$", 2)
        return compare_digest(hash_password(password, salt).split("$")[-1], digest)
    except ValueError:
        return False


def create_token(user: User) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode(
        {
            "sub": user.id,
            "role": user.role,
            "ver": user.token_version,
            "jti": token_hex(16),
            "iat": datetime.now(timezone.utc),
            "exp": expires,
        },
        settings.secret_key,
        algorithm="HS256",
    )


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    if not payload.get("sub") or not payload.get("jti"):
        raise HTTPException(401, "Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    return payload


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not credentials:
        raise HTTPException(401, "Authentication required", headers={"WWW-Authenticate": "Bearer"})
    payload = decode_token(credentials.credentials)
    identity = (
        db.query(User, RevokedToken.id)
        .outerjoin(RevokedToken, RevokedToken.id == payload["jti"])
        .filter(User.id == payload.get("sub"))
        .first()
    )
    if identity and identity[1] is not None:
        raise HTTPException(401, "Session has been signed out", headers={"WWW-Authenticate": "Bearer"})
    user = identity[0] if identity else None
    if not user or not user.is_active or user.is_test_account:
        raise HTTPException(401, "Session is inactive or unavailable", headers={"WWW-Authenticate": "Bearer"})
    if payload.get("ver", 0) != user.token_version:
        raise HTTPException(401, "Session is no longer valid", headers={"WWW-Authenticate": "Bearer"})
    return user


def require_roles(*roles: str):
    def dependency(
        request: Request,
        user: User = Depends(current_user),
        db: Session = Depends(get_db),
    ) -> User:
        if user.must_change_password:
            raise HTTPException(403, "Password change required")
        if user.role == "owner":
            return user
        module = module_for_request(request)
        if module:
            override = explicit_permission(db, user.id, module, action_for_request(request))
            if override is not None:
                if override:
                    return user
                raise HTTPException(403, "You do not have permission to perform this action")
        if user.role not in roles:
            raise HTTPException(403, "You do not have permission to perform this action")
        return user
    return dependency
