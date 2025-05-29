from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class SensorReading:
    id: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    temp: float = 0.0
    hum: float = 0.0
    soil: int = 0
    light: int = 0
    dist: int = 0
    motion: bool = False
    acc_x: int = 0
    acc_y: int = 0
    acc_z: int = 0

@dataclass
class GreenhouseSettings:
    id: Optional[int] = None
    owner: str = ""
    name: str = ""
    temp_min: float = 0.0
    temp_max: float = 0.0
    light_min: float = 0.0
    light_max: float = 0.0
    hum_min: float = 0.0
    hum_max: float = 0.0
    soil_min: int = 0

@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    is_first_login: bool = True

@dataclass
class RevokedToken:
    jti: str
    revoked_at: datetime = field(default_factory=datetime.utcnow)
