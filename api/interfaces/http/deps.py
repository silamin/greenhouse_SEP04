from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from db import SessionLocal
from adapters.db.repositories import UserRepository, TokenBlacklistRepository
from security import SECRET_KEY, ALGORITHM
from domain.entities import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(db_session)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        jti: str = payload.get("jti")
        if username is None or jti is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    if TokenBlacklistRepository(db).is_revoked(jti):
        raise credentials_exception
    user = UserRepository(db).get(username)
    if user is None:
        raise credentials_exception
    return {"username": user.username, "jti": jti, "is_first_login": user.is_first_login}
