from adapters.db.repositories import UserRepository, TokenBlacklistRepository
from use_cases.auth_service import AuthService


def test_authenticate_and_change_password(db_session):
    user_repo = UserRepository(db_session)
    blacklist = TokenBlacklistRepository(db_session)
    auth = AuthService(user_repo, blacklist)

    # create admin
    user_repo.upsert_admin("admin", "secret")

    # correct / wrong password
    assert auth.authenticate("admin", "secret") is not None
    assert auth.authenticate("admin", "wrong") is None

    # change pwd
    auth.change_password("admin", "newsecret")
    assert auth.authenticate("admin", "secret") is None
    assert auth.authenticate("admin", "newsecret") is not None
