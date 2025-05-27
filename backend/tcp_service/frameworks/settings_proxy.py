import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from api_service.adapters.models import SettingsDB
from common.models import GreenhouseSettings

# Support both old “postgres://” and new “postgresql://” schemes
_DATABASE_URL = os.getenv("DATABASE_URL", "")
if _DATABASE_URL.startswith("postgres://"):
    _DATABASE_URL = _DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class SettingsProxy:
    """Read-only access to greenhouse threshold settings."""
    def __init__(self):
        self.db: Session = SessionLocal()

    def get(self, owner: str):
        row = self.db.query(SettingsDB).filter_by(owner=owner).first()
        return None if row is None else GreenhouseSettings(**row.__dict__)
