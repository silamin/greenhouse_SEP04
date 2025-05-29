from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SensorReading:
    id: Optional[int]
    timestamp: datetime
    temp: float
    hum: float
    soil: int
    light: int
    dist: int
    motion: bool
    acc_x: int
    acc_y: int
    acc_z: int


@dataclass
class GreenhouseSettings:
    owner: str
    name: str
    temp_min: float
    temp_max: float
    light_min: float
    light_max: float
    hum_min: float
    hum_max: float
    soil_min: int
