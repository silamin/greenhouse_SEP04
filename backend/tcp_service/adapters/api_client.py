import os
import httpx
from domain.entities import SensorReading

API_BASE = os.getenv("API_BASE_URL", "http://api_service:80")

class APIClient:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=API_BASE, timeout=5.0)

    async def send_reading(self, reading: SensorReading):
        payload = {
            "timestamp": reading.timestamp.isoformat(),
            "temp": reading.temp,
            "hum": reading.hum,
            "soil": reading.soil,
            "light": reading.light,
            "dist": reading.dist,
            "motion": reading.motion,
            "acc_x": reading.acc_x,
            "acc_y": reading.acc_y,
            "acc_z": reading.acc_z,
        }
        resp = await self.client.post("/sensors/", json=payload)
        resp.raise_for_status()
        return resp.json()
