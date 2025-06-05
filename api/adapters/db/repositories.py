# adapters/db/repositories.py
from typing import List, Optional
from sqlalchemy.orm import Session
from domain.entities import (
    SensorReading,
    GreenhouseSettings,
    User,
    RevokedToken,
)
from adapters.db.models import (
    SensorDB,
    SettingsDB,
    LoginDB,
    RevokedTokenDB,
)
from security import get_password_hash


class SensorRepository:
    def __init__(self, db: Session):
        self.db = db

    def insert(self, r: SensorReading) -> SensorReading:
        row = SensorDB(**r.__dict__)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)

        # Filter out SQLAlchemy internals before passing to dataclass
        data = {k: v for k, v in row.__dict__.items() if not k.startswith("_")}
        return SensorReading(**data)

    def fetch_all(self, skip=0, limit=100) -> List[SensorReading]:
        rows = self.db.query(SensorDB).offset(skip).limit(limit).all()
        result = []
        for row in rows:
            data = {k: v for k, v in row.__dict__.items() if not k.startswith("_")}
            result.append(SensorReading(**data))
        return result

    def fetch_by_time(self, from_time, to_time) -> List[SensorReading]:
        rows = (
            self.db.query(SensorDB)
            .filter(SensorDB.timestamp >= from_time, SensorDB.timestamp <= to_time)
            .order_by(SensorDB.timestamp)
            .all()
        )
        result = []
        for row in rows:
            data = {k: v for k, v in row.__dict__.items() if not k.startswith("_")}
            result.append(SensorReading(**data))
        return result


class SettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, owner: str) -> Optional[GreenhouseSettings]:
        row = self.db.query(SettingsDB).filter_by(owner=owner).first()
        if not row:
            return None
        data = {k: v for k, v in row.__dict__.items() if not k.startswith("_")}
        return GreenhouseSettings(**data)

    def upsert(self, s: GreenhouseSettings) -> GreenhouseSettings:
        row = self.db.query(SettingsDB).filter_by(owner=s.owner).first()
        if not row:
            row = SettingsDB(**s.__dict__)
            self.db.add(row)
        else:
            for k, v in s.__dict__.items():
                if k == "id":
                    continue
                setattr(row, k, v)
        self.db.commit()
        self.db.refresh(row)

        data = {k: v for k, v in row.__dict__.items() if not k.startswith("_")}
        return GreenhouseSettings(**data)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, username: str) -> Optional[User]:
        row = self.db.query(LoginDB).filter_by(username=username).first()
        if not row:
            return None

        data = {k: v for k, v in row.__dict__.items() if not k.startswith("_")}
        return User(
            id=data["id"],
            username=data["username"],
            password_hash=data["password_hash"],
            is_first_login=data["is_first_login"],
        )

    def upsert_admin(self, username: str, password: str) -> User:
        row = self.db.query(LoginDB).filter_by(username=username).first()
        pw_hash = get_password_hash(password)
        if not row:
            row = LoginDB(username=username, password_hash=pw_hash, is_first_login=True)
            self.db.add(row)
        else:
            row.password_hash = pw_hash
            row.is_first_login = True
        self.db.commit()
        self.db.refresh(row)

        data = {k: v for k, v in row.__dict__.items() if not k.startswith("_")}
        return User(
            id=data["id"],
            username=data["username"],
            password_hash=data["password_hash"],
            is_first_login=data["is_first_login"],
        )

    def change_password(self, username: str, new_password: str):
        row = self.db.query(LoginDB).filter_by(username=username).first()
        if row:
            row.password_hash = get_password_hash(new_password)
            row.is_first_login = False
            self.db.commit()


class TokenBlacklistRepository:
    def __init__(self, db: Session):
        self.db = db

    def revoke(self, jti: str):
        self.db.add(RevokedTokenDB(jti=jti))
        self.db.commit()

    def is_revoked(self, jti: str) -> bool:
        return (
            self.db.query(RevokedTokenDB).filter_by(jti=jti).first()
            is not None
        )
