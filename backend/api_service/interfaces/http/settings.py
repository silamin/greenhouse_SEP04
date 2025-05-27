from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api_service.adapters.models import LoginDB
from api_service.adapters.repositories import SettingsRepository
from api_service.interfaces.http.schemas import SettingsOut, SettingsIn
from api_service.security import get_current_user
from api_service.use_cases.settings_service import SettingsService
from common.models import GreenhouseSettings
from api_service.interfaces.http.deps import db_session

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/", response_model=SettingsOut)
def read(
        u=Depends(get_current_user),
        db: Session = Depends(db_session),
):
    repo = SettingsRepository(db)
    svc = SettingsService(repo)
    s = svc.get(u["username"])
    if not s:
        raise HTTPException(404, "Settings not found")
    return s


@router.post("/", response_model=SettingsOut)
def write(
        d: SettingsIn,
        u=Depends(get_current_user),
        db: Session = Depends(db_session),
):
    repo = SettingsRepository(db)
    svc = SettingsService(repo)
    gh = GreenhouseSettings(
        owner=u["username"],
        name=d.name,
        temp_min=d.temp_min,
        temp_max=d.temp_max,
        light_min=d.light_min,
        light_max=d.light_max,
        hum_min=d.hum_min,
        hum_max=d.hum_max,
        soil_min=d.soil_min,
    )
    return svc.save(gh)


@router.post("/", response_model=SettingsOut)
def write(
        d: SettingsIn,
        u=Depends(get_current_user),
        db: Session = Depends(db_session),
):
    # Save new settings
    repo = SettingsRepository(db)
    svc = SettingsService(repo)
    gh = GreenhouseSettings(
        owner=u["username"],
        name=d.name,
        temp_min=d.temp_min,
        temp_max=d.temp_max,
        light_min=d.light_min,
        light_max=d.light_max,
        hum_min=d.hum_min,
        hum_max=d.hum_max,
        soil_min=d.soil_min,
    )
    saved = svc.save(gh)

    # 👇 Mark first login complete
    user = db.query(LoginDB).filter_by(username=u["username"]).first()
    if user and user.is_first_login:
        user.is_first_login = False
        db.commit()

    return saved
