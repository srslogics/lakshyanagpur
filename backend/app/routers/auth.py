from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import RevokedToken, User
from ..schemas import BootstrapOwnerRequest, LoginRequest, TokenResponse
from ..security import bearer, create_token, current_user, decode_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["authentication"])


def _token_response(user: User):
    return {
        "access_token": create_token(user),
        "expires_in": settings.access_token_minutes * 60,
        "user": {
            "id": user.id,
            "email": user.email,
            "fullName": user.full_name,
            "role": user.role,
        },
    }


@router.get("/bootstrap-status")
def bootstrap_status(db: Session = Depends(get_db)):
    return {"setupRequired": db.query(User).count() == 0}


@router.post("/bootstrap", response_model=TokenResponse, status_code=201)
def bootstrap_owner(payload: BootstrapOwnerRequest, db: Session = Depends(get_db)):
    if db.query(User).count() > 0:
        raise HTTPException(409, "Initial owner setup has already been completed")
    user = User(email=payload.email.lower(), full_name=payload.full_name, role="owner", password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return _token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash) or not user.is_active:
        raise HTTPException(401, "Invalid email or password")
    return _token_response(user)


@router.get("/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "email": user.email, "fullName": user.full_name, "role": user.role}


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
