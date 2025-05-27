from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, Annotated
import re

# ------------------------------
# Sensor Models
# ------------------------------

class SensorDataBase(BaseModel):
    temp: float
    hum: float
    soil: int
    light: int
    dist: int
    motion: bool
    acc_x: int
    acc_y: int
    acc_z: int


class SensorDataCreate(SensorDataBase):
    timestamp: Optional[datetime] = None


class SensorDataRead(SensorDataBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True  # ✅ Required for .from_orm() in Pydantic v2


# ------------------------------
# Settings Models
# ------------------------------

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
    owner: str

    class Config:
        from_attributes = True  # ✅ Pydantic v2


# ------------------------------
# Change Password Schema (Pydantic v2 style)
# ------------------------------

PasswordStr = Annotated[str, lambda v: (
    re.fullmatch(r'^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$', v)
    or ValueError("Password must be at least 8 characters, include 1 uppercase, 1 number, and 1 special character.")
)]

class ChangePasswordRequest(BaseModel):
    new_password: PasswordStr
    confirm_password: str

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        new_pw = info.data.get('new_password')
        if v != new_pw:
            raise ValueError("Passwords do not match")
        return v
