import datetime
from sqlalchemy import text
from common.models import SensorReading, GreenhouseSettings
from .models import SensorDB, SettingsDB


class SensorRepository:
    def __init__(self, db):
        self.db = db

    def insert(self, r: SensorReading) -> SensorReading:
        row = SensorDB(
            temp=r.temp,
            hum=r.hum,
            soil=r.soil,
            light=r.light,
            dist=r.dist,
            motion=r.motion,
            acc_x=r.acc_x,
            acc_y=r.acc_y,
            acc_z=r.acc_z,
            timestamp=r.timestamp or datetime.datetime.utcnow(),
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return SensorReading(**row.__dict__)

    def fetch_all(self, skip=0, limit=100):
        rows = (
            self.db
            .query(SensorDB)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [
            SensorReading(
                id=row.id,
                timestamp=row.timestamp,
                temp=row.temp,
                hum=row.hum,
                soil=row.soil,
                light=row.light,
                dist=row.dist,
                motion=row.motion,
                acc_x=row.acc_x,
                acc_y=row.acc_y,
                acc_z=row.acc_z
            )
            for row in rows
        ]

    def fetch_by_time(self, from_time: datetime, to_time: datetime):
        rows = (
            self.db.query(SensorDB)
            .filter(SensorDB.timestamp >= from_time, SensorDB.timestamp <= to_time)
            .order_by(SensorDB.timestamp.asc())
            .all()
        )
        return [
            SensorReading(
                id=row.id,
                timestamp=row.timestamp,
                temp=row.temp,
                hum=row.hum,
                soil=row.soil,
                light=row.light,
                dist=row.dist,
                motion=row.motion,
                acc_x=row.acc_x,
                acc_y=row.acc_y,
                acc_z=row.acc_z
            )
            for row in rows
        ]


class SettingsRepository:
    def __init__(self, db):
        self.db = db

    def get(self, owner: str) -> SettingsDB | None:
        return self.db.query(SettingsDB).filter_by(owner=owner).first()

    def upsert(self, s: GreenhouseSettings) -> SettingsDB:
        row = self.db.query(SettingsDB).filter_by(owner=s.owner).first()
        if not row:
            row = SettingsDB(**s.__dict__)
            self.db.add(row)
        else:
            for k, v in s.__dict__.items():
                setattr(row, k, v)
        self.db.commit()
        return row
