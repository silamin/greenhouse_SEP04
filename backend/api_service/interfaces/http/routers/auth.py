from fastapi import APIRouter, Depends, HTTPException
from datetime import timedelta

from interfaces.http.schemas import (
    LoginRequest, LoginResponse, LogoutResponse, ChangePasswordRequest
)
from interfaces.http.deps import db_session, get_current_user
from adapters.db.repositories import UserRepository, TokenBlacklistRepository
from use_cases.auth_service import AuthService
from security import (
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token", response_model=LoginResponse)
def login(payload: LoginRequest, db=Depends(db_session)):
    user_repo = UserRepository(db)
    blk = TokenBlacklistRepository(db)
    auth = AuthService(user_repo, blk)

    user = auth.authenticate(payload.username, payload.password)
    if not user:
        raise HTTPException(400, "Invalid credentials")

    expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token({"sub": user.username}, expires)
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        is_first_login=user.is_first_login
    )

@router.post("/logout", response_model=LogoutResponse)
def logout(ctx=Depends(get_current_user), db=Depends(db_session)):
    _, jti = ctx["username"], ctx["jti"]
    blk = TokenBlacklistRepository(db)
    auth = AuthService(UserRepository(db), blk)
    auth.revoke_token(jti)
    return LogoutResponse(message=f"User '{ctx['username']}' logged out.")

@router.post("/change-password", response_model=LogoutResponse)
def change_password(
    payload: ChangePasswordRequest,
    ctx=Depends(get_current_user),
    db=Depends(db_session)
):
    auth = AuthService(UserRepository(db), TokenBlacklistRepository(db))
    auth.change_password(ctx["username"], payload.new_password)
    return LogoutResponse(message="Password updated")
