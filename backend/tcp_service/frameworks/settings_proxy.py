import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from adapters.db.models import SettingsDB
from domain.entities import GreenhouseSettings

_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class SettingsProxy:
    """Read-only access to greenhouse threshold settings from the same DB."""
    def __init__(self):
        self.db: Session = SessionLocal()

    def get(self, owner: str) -> GreenhouseSettings | None:
        row = self.db.query(SettingsDB).filter_by(owner=owner).first()
        if not row:
            return None
        return GreenhouseSettings(
            owner=row.owner, name=row.name,
            temp_min=row.temp_min, temp_max=row.temp_max,
            light_min=row.light_min, light_max=row.light_max,
            hum_min=row.hum_min, hum_max=row.hum_max,
            soil_min=row.soil_min
        )
