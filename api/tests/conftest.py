# tests/conftest.py
import os
os.environ["TESTING"] = "1"   # ← ensure main.py skips its startup‐time create_all

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from db import Base
from main import app
from adapters.db.repositories import UserRepository

# Import the dependency functions from their actual locations:
from interfaces.http import deps
from interfaces.http.routers import auth as auth_router
from interfaces.http.routers import sensors as sensors_router
from interfaces.http.routers import settings as settings_router

# ---------------------------------------------------------------------------
# 1) Create a single in‐memory SQLite engine for all tests in this session.
#    We call Base.metadata.create_all(eng) here so that the schema is available.
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
# 2) Build a TestClient(app) and override EVERY db_session dependency to use SQLite.
# ---------------------------------------------------------------------------
@pytest.fixture(scope="function")
def client(db_session):
    def _test_db():
        # Signature matches FastAPI's expected "get_db" generator
        try:
            yield db_session
        finally:
            pass

    # --- Override the dependency in deps.py directly ---
    app.dependency_overrides[deps.db_session] = _test_db

    # --- Override the copy of db_session that each router imported at import‐time ---
    app.dependency_overrides[auth_router.db_session] = _test_db
    app.dependency_overrides[sensors_router.db_session] = _test_db
    app.dependency_overrides[settings_router.db_session] = _test_db

    return TestClient(app)


# ---------------------------------------------------------------------------
# 3) Convenience fixture: a default admin user in SQLite before each test.
# ---------------------------------------------------------------------------
@pytest.fixture(scope="function")
def admin_user(db_session):
    repo = UserRepository(db_session)
    return repo.upsert_admin("admin", "secret")
