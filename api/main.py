from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import engine, Base
from adapters.db import models      # noqa: F401  (ensures SQLAlchemy sees all your models)
from interfaces.http.routers import auth, sensors, settings

app = FastAPI(title="Greenhouse Cloud API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# NOTE: We’ve REMOVED every `Base.metadata.create_all(bind=engine)` from here.
#       Tests will create tables in SQLite entirely via `conftest.py`.
# ─────────────────────────────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(sensors.router)
app.include_router(settings.router)


@app.get("/health")
def health():
    return {"status": "ok"}
