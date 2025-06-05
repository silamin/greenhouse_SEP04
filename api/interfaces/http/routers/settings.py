from fastapi import APIRouter, Depends, HTTPException

from interfaces.http.schemas import SettingsIn, SettingsOut
from adapters.db.repositories import SettingsRepository
from use_cases.settings_service import SettingsService
from domain.entities import GreenhouseSettings
from interfaces.http.deps import db_session, get_current_user

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("/", response_model=SettingsOut)
def read_settings(db=Depends(db_session), user=Depends(get_current_user)):
    svc = SettingsService(SettingsRepository(db))
    s = svc.get(user["username"])
    if not s:
        raise HTTPException(404, "Settings not found")
    return SettingsOut(**s.__dict__)

@router.post("/", response_model=SettingsOut)
def write_settings(payload: SettingsIn,
                   db=Depends(db_session), user=Depends(get_current_user)):
    svc = SettingsService(SettingsRepository(db))
    gh = GreenhouseSettings(
        owner=user["username"],
        name=payload.name,
        temp_min=payload.temp_min,
        temp_max=payload.temp_max,
        light_min=payload.light_min,
        light_max=payload.light_max,
        hum_min=payload.hum_min,
        hum_max=payload.hum_max,
        soil_min=payload.soil_min
    )
    saved = svc.save(gh)
    return SettingsOut(**saved.__dict__)
