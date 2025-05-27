from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column, Integer, Float, Boolean, DateTime,
    String, func
)
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

Base = declarative_base()


class RevokedTokenDB(Base):
    __tablename__ = "revoked_tokens"
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, nullable=False)
    revoked_at = Column(DateTime, default=datetime.utcnow)


class SensorDB(Base):
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    temp = Column(Float)
    hum = Column(Float)
    soil = Column(Integer)
    light = Column(Integer)
    dist = Column(Integer)
    motion = Column(Boolean)

    # New fields for accelerometer data
    acc_x = Column(Integer)
    acc_y = Column(Integer)
    acc_z = Column(Integer)


class SettingsDB(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    owner = Column(String, unique=True)
    name = Column(String)

    temp_min = Column(Float)
    temp_max = Column(Float)
    light_min = Column(Float)
    light_max = Column(Float)
    hum_min = Column(Float)
    hum_max = Column(Float)
    soil_min = Column(Integer)


class LoginDB(Base):
    __tablename__ = "login"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_first_login = Column(Boolean, default=True)
