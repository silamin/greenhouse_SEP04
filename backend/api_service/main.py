from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api_service.interfaces.http.sensors import router as sensors
from api_service.interfaces.http.auth import router as auth
from api_service.interfaces.http.settings import router as settings

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


@app.get("/health")
def health():
    return {"status": "ok"}
