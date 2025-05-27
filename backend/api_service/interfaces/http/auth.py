from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api_service.interfaces.http.schemas import ChangePasswordRequest
from api_service.security import authenticate_user, create_token, get_current_user, hash_password
from api_service.db import SessionLocal
from api_service.adapters.models import RevokedTokenDB, LoginDB
from fastapi import Depends

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/token")
async def login(credentials: LoginRequest):
    user = authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_token({"sub": user["username"]})
    db = SessionLocal()
    try:
        user_obj = db.query(LoginDB).filter_by(username=credentials.username).first()
        return {
            "access_token": token,
            "token_type": "bearer",
            "is_first_login": user_obj.is_first_login,
        }
    finally:
        db.close()


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    db = SessionLocal()
    try:
        db.add(RevokedTokenDB(token=current_user["jti"]))
        db.commit()
        return {"message": f"User '{current_user['username']}' logged out and token revoked."}
    finally:
        db.close()


@router.post("/auth/change-password")
def change_password(
        payload: ChangePasswordRequest,
        current_user: dict = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        user = db.query(LoginDB).filter_by(username=current_user["username"]).first()
        user.password_hash = hash_password(payload.new_password)
        user.is_first_login = False
        db.commit()
        return {"message": "Password updated"}
    finally:
        db.close()
