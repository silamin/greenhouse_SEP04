from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import re

# --- Sensors ---
class SensorDataCreate(BaseModel):
    timestamp: Optional[datetime]
    temp: float
    hum: float
    soil: int
    light: int
    dist: int
    motion: bool
    acc_x: int
    acc_y: int
    acc_z: int

class SensorDataRead(SensorDataCreate):
    id: int
    timestamp: datetime

# --- Settings ---
class SettingsIn(BaseModel):
    name: str
    temp_min: float
    temp_max: float
    light_min: float
    light_max: float
    hum_min: float
    hum_max: float
    soil_min: int

class SettingsOut(SettingsIn):
    id: int
    owner: str

# --- Auth ---
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    is_first_login: bool

class LogoutResponse(BaseModel):
    message: str

PasswordStr = str

class ChangePasswordRequest(BaseModel):
    new_password: PasswordStr
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if v != info.data.get("new_password"):
            raise ValueError("Passwords do not match")
        return v
