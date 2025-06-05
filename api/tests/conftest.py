import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from db import Base
from main import app
from adapters.db.repositories import UserRepository


# ---------------------------------------------------------------------------
# Database & session fixture
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def _engine():
    eng = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture(scope="function")
def db_session(_engine):
    connection = _engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


# ---------------------------------------------------------------------------
# FastAPI TestClient with dependency override
# ---------------------------------------------------------------------------
@pytest.fixture(scope="function")
def client(db_session, monkeypatch):
    from interfaces.http import deps  # local import avoids circular refs

    def _test_db():
        # exact same signature FastAPI expects
        try:
            yield db_session
        finally:
            pass

    monkeypatch.setattr(deps, "db_session", _test_db)
    return TestClient(app)


# ---------------------------------------------------------------------------
# Convenience fixture: a default admin user
# ---------------------------------------------------------------------------
@pytest.fixture(scope="function")
def admin_user(db_session):
    repo = UserRepository(db_session)
    return repo.upsert_admin("admin", "secret")
