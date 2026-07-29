from collections import deque
from datetime import datetime, timezone
from threading import Lock
from time import monotonic

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..identity import normalize_mobile
from ..models import RevokedToken, User
from ..schemas import BootstrapOwnerRequest, LoginRequest, PasswordChangeRequest, TokenResponse
from ..security import bearer, create_token, current_user, decode_token, hash_password, verify_password
from ..services import audit

router = APIRouter(prefix="/api/auth", tags=["authentication"])
LOGIN_FAILURE_LIMIT = 8
LOGIN_FAILURE_WINDOW_SECONDS = 10 * 60
_login_failures: dict[str, deque[float]] = {}
_login_failures_lock = Lock()


def _login_key(request: Request, payload: LoginRequest) -> str:
    identity = normalize_mobile(payload.mobile) if payload.mobile else str(payload.email or "").strip().lower()
    client_host = request.client.host if request.client else "unknown"
    return f"{client_host}:{identity or 'unknown'}"


def _prune_failures(key: str, now: float) -> deque[float]:
    failures = _login_failures.setdefault(key, deque())
    cutoff = now - LOGIN_FAILURE_WINDOW_SECONDS
    while failures and failures[0] <= cutoff:
        failures.popleft()
    if not failures:
        _login_failures.pop(key, None)
        return deque()
    return failures


def _check_login_rate_limit(key: str) -> None:
    now = monotonic()
    with _login_failures_lock:
        failures = _prune_failures(key, now)
        if len(failures) < LOGIN_FAILURE_LIMIT:
            return
        retry_after = max(1, int(LOGIN_FAILURE_WINDOW_SECONDS - (now - failures[0])))
    raise HTTPException(
        429,
        "Too many sign-in attempts. Please wait before trying again.",
        headers={"Retry-After": str(retry_after)},
    )


def _record_login_failure(key: str) -> None:
    now = monotonic()
    with _login_failures_lock:
        failures = _prune_failures(key, now)
        failures.append(now)
        _login_failures[key] = failures


def _clear_login_failures(key: str) -> None:
    with _login_failures_lock:
        _login_failures.pop(key, None)


def _token_response(user: User):
    return {
        "access_token": create_token(user),
        "expires_in": settings.access_token_minutes * 60,
        "user": {
            "id": user.id,
            "mobile": user.mobile,
            "email": user.email,
            "fullName": user.full_name,
            "role": user.role,
            "mustChangePassword": user.must_change_password,
        },
    }


@router.get("/bootstrap-status")
def bootstrap_status(db: Session = Depends(get_db)):
    return {
        "setupRequired": db.query(User).filter(User.role == "owner").count() == 0,
        "allowLegacyEmailLogin": settings.allow_legacy_email_login,
    }


@router.post("/bootstrap", response_model=TokenResponse, status_code=201)
def bootstrap_owner(payload: BootstrapOwnerRequest, db: Session = Depends(get_db)):
    if db.get_bind().dialect.name == "postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(202600002)"))
    if db.query(User).filter(User.role == "owner").count() > 0:
        raise HTTPException(409, "Initial owner setup has already been completed")
    user = User(
        mobile=payload.mobile,
        email=str(payload.email).lower() if payload.email else None,
        full_name=payload.full_name,
        role="owner",
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    login_key = _login_key(request, payload)
    _check_login_rate_limit(login_key)
    if payload.mobile:
        user = db.query(User).filter(User.mobile == normalize_mobile(payload.mobile)).first()
    elif payload.email:
        candidate = db.query(User).filter(User.email == str(payload.email).lower()).first()
        faculty_first_login = bool(
            candidate
            and candidate.role == "faculty"
            and not candidate.mobile
        )
        user = candidate if faculty_first_login or settings.allow_legacy_email_login else None
    else:
        user = None
    if not user or not verify_password(payload.password, user.password_hash) or not user.is_active:
        _record_login_failure(login_key)
        raise HTTPException(401, "Invalid sign-in details")
    _clear_login_failures(login_key)
    return _token_response(user)


@router.get("/me")
def me(user: User = Depends(current_user)):
    return {
        "id": user.id,
        "mobile": user.mobile,
        "email": user.email,
        "fullName": user.full_name,
        "role": user.role,
        "mustChangePassword": user.must_change_password,
    }


@router.post("/change-password", status_code=204)
def change_password(
    payload: PasswordChangeRequest,
    response: Response,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(400, "Current password is incorrect")
    if verify_password(payload.new_password, user.password_hash):
        raise HTTPException(400, "Choose a new password different from the temporary password")
    user.password_hash = hash_password(payload.new_password)
    user.must_change_password = False
    user.token_version += 1
    token = decode_token(credentials.credentials)
    expires_at = datetime.fromtimestamp(token["exp"], timezone.utc)
    db.add(RevokedToken(id=token["jti"], user_id=user.id, expires_at=expires_at))
    audit(
        db,
        user,
        "auth.password.change",
        "user",
        user.id,
        after={"mustChangePassword": False},
    )
    db.commit()
    response.status_code = 204


@router.post("/logout", status_code=204)
def logout(
    response: Response,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    payload = decode_token(credentials.credentials)
    expires_at = datetime.fromtimestamp(payload["exp"], timezone.utc)
    db.add(RevokedToken(id=payload["jti"], user_id=user.id, expires_at=expires_at))
    db.commit()
    response.status_code = 204
