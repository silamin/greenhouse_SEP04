import os, asyncio
import httpx
from datetime import datetime, timedelta

from domain.entities import SensorReading

API_BASE    = os.getenv("API_BASE_URL",    "http://api_service:80")
AUTH_USER   = os.getenv("API_AUTH_USER",   "tcp_worker")
AUTH_PASS   = os.getenv("API_AUTH_PASS",   "supersecret")
TOKEN_TTL   = int(os.getenv("API_TOKEN_TTL", "1800"))  # seconds

class APIClient:
    def __init__(self):
        self.client  = httpx.AsyncClient(base_url=API_BASE, timeout=5.0)
        self.token: str | None = None
        self.expires_at: datetime = datetime.utcnow()
        self._lock = asyncio.Lock()

    async def _authenticate(self):
        """Fetch a fresh JWT from /auth/token."""
        # Note: fastapi’s OAuth2PasswordRequestForm expects form data
        resp = await self.client.post(
            "/auth/token",
            data={"username": AUTH_USER, "password": AUTH_PASS},
        )
        resp.raise_for_status()
        body = resp.json()
        self.token = body["access_token"]
        # assume TTL roughly known; if the token payload has exp you could decode it
        self.expires_at = datetime.utcnow() + timedelta(seconds=TOKEN_TTL)
        # set header for future calls
        self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    async def _ensure_token(self):
        # avoid race on startup
        async with self._lock:
            if not self.token or datetime.utcnow() >= self.expires_at:
                await self._authenticate()

    async def send_reading(self, reading: SensorReading):
        await self._ensure_token()
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

        # if our token expired server-side, refresh & retry once
        if resp.status_code == 401:
            await self._authenticate()
            resp = await self.client.post("/sensors/", json=payload)

        resp.raise_for_status()
        return resp.json()
