from datetime import datetime
from sqlalchemy import (
    Column, Integer, Float, Boolean, DateTime, String, func
)
from db import Base

class SensorDB(Base):
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    temp = Column(Float)
    hum = Column(Float)
    soil = Column(Integer)
    light = Column(Integer)
    dist = Column(Integer)
    motion = Column(Boolean)
    acc_x = Column(Integer)
    acc_y = Column(Integer)
    acc_z = Column(Integer)

class SettingsDB(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    owner = Column(String, unique=True, index=True)
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
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_first_login = Column(Boolean, default=True)

class RevokedTokenDB(Base):
    __tablename__ = "revoked_tokens"
    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, index=True, nullable=False)
    revoked_at = Column(DateTime, default=datetime.utcnow)
