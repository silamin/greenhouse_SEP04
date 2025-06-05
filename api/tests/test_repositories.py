from datetime import datetime, timedelta

from adapters.db.repositories import (
    SensorRepository,
    SettingsRepository,
    TokenBlacklistRepository,
)
from domain.entities import SensorReading, GreenhouseSettings


def test_sensor_insert_and_fetch(db_session):
    repo = SensorRepository(db_session)
    saved = repo.insert(
        SensorReading(
            temp=22.5,
            hum=55.0,
            soil=300,
            light=650,
            dist=10,
            motion=False,
            acc_x=1,
            acc_y=2,
            acc_z=3,
        )
    )
    assert saved.id is not None

    fetched = repo.fetch_all()
    assert len(fetched) == 1
    assert fetched[0].temp == 22.5


def test_sensor_fetch_by_time(db_session):
    repo = SensorRepository(db_session)
    now = datetime.utcnow()
    repo.insert(
        SensorReading(
            timestamp=now - timedelta(minutes=10),
            temp=20,
            hum=40,
            soil=250,
            light=500,
            dist=10,
            motion=False,
            acc_x=0,
            acc_y=0,
            acc_z=0,
        )
    )
    repo.insert(
        SensorReading(
            timestamp=now,
            temp=21,
            hum=41,
            soil=260,
            light=510,
            dist=10,
            motion=False,
            acc_x=0,
            acc_y=0,
            acc_z=0,
        )
    )
    rows = repo.fetch_by_time(now - timedelta(minutes=5), now + timedelta(minutes=1))
    assert [r.temp for r in rows] == [21]


def test_settings_upsert_and_get(db_session):
    repo = SettingsRepository(db_session)
    config = GreenhouseSettings(
        owner="alice",
        name="GH-1",
        temp_min=18,
        temp_max=28,
        light_min=300,
        light_max=700,
        hum_min=40,
        hum_max=60,
        soil_min=200,
    )
    repo.upsert(config)
    assert repo.get("alice").temp_max == 28

    # update
    config.temp_max = 30
    repo.upsert(config)
    assert repo.get("alice").temp_max == 30


def test_token_blacklist(db_session):
    repo = TokenBlacklistRepository(db_session)
    jti = "random-jti"
    assert repo.is_revoked(jti) is False
    repo.revoke(jti)
    assert repo.is_revoked(jti) is True
