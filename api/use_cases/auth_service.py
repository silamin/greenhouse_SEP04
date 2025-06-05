from typing import Optional
from domain.entities import User
from adapters.db.repositories import UserRepository, TokenBlacklistRepository
from security import verify_password

class AuthService:
    def __init__(self, user_repo: UserRepository, blacklist_repo: TokenBlacklistRepository):
        self.user_repo = user_repo
        self.blacklist_repo = blacklist_repo

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.user_repo.get(username)
        if user and verify_password(password, user.password_hash):
            return user
        return None

    def revoke_token(self, jti: str):
        self.blacklist_repo.revoke(jti)

    def change_password(self, username: str, new_password: str):
        self.user_repo.change_password(username, new_password)
