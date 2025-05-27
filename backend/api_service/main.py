from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_service.adapters.repositories import SensorRepository
from api_service.db import SessionLocal
from api_service.interfaces.http.sensors import router as sensors
from api_service.interfaces.http.auth import router as auth
from api_service.interfaces.http.settings import router as settings
from common.models import SensorReading
from common import messaging

app = FastAPI(title="Greenhouse Cloud API")
# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include routers
app.include_router(auth)
app.include_router(sensors)
app.include_router(settings)  # <- This must exist!


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


@app.on_event("startup")
async def on_startup():
    db = SessionLocal()
    repo = SensorRepository(db)

    async def persist(payload: dict):
        reading = SensorReading(**payload)
        repo.insert(reading)

    messaging.message_handler = messaging.build_handler(persist)
    await messaging.init_nats()


@app.on_event("shutdown")
async def on_shutdown():
    await messaging.close_nats()
