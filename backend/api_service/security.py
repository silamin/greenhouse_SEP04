import os
from datetime import datetime, timedelta
from typing import Optional
import uuid

import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from api_service.db import SessionLocal
from api_service.adapters.models import LoginDB, RevokedTokenDB

oauth2 = OAuth2PasswordBearer(tokenUrl="token")

SECRET = os.getenv("JWT_SECRET", "changeme")
ALGO = "HS256"
EXPIRE = 60  # minutes


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def authenticate_user(username: str, password: str) -> Optional[dict]:
    db = SessionLocal()
    try:
        user = db.query(LoginDB).filter_by(username=username).first()
        if user and verify(password, user.password_hash):
            return {"username": user.username}
    finally:
        db.close()
    return None


def create_token(data: dict, exp: int | None = None) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=exp or EXPIRE)
    payload["jti"] = str(uuid.uuid4())  # unique token ID
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def get_current_user(token: str = Depends(oauth2)) -> dict:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        username = payload.get("sub")
        jti = payload.get("jti")
        if username is None or jti is None:
            raise exc
    except JWTError:
        raise exc

    db = SessionLocal()
    try:
        # Check token blacklist
        if db.query(RevokedTokenDB).filter_by(token=jti).first():
            raise exc

        user = db.query(LoginDB).filter_by(username=username).first()
        if not user:
            raise exc
        return {"username": user.username, "jti": jti}
    finally:
        db.close()