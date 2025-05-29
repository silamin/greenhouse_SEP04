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
    owner: str
    name: str
    temp_min: float
    temp_max: float
    light_min: float
    light_max: float
    hum_min: float
    hum_max: float
    soil_min: int

@dataclass
class DeviceCommand:
    device: str
    action: str
    timestamp: Optional[datetime] = None
