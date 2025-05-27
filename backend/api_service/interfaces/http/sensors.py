from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from common.models import SensorReading
from api_service.adapters.repositories import SensorRepository
from api_service.interfaces.http.schemas import SensorDataRead
from api_service.security import get_current_user
from api_service.interfaces.http.deps import db_session

from datetime import datetime
from fastapi import Query

router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.get("/", response_model=List[SensorDataRead])
async def read_sensors(
        skip: int = 0,
        limit: int = 100,
        user=Depends(get_current_user),
        db: Session = Depends(db_session),
):
    repo = SensorRepository(db)
    return repo.fetch_all(skip, limit)


@router.get("/history", response_model=List[SensorDataRead])
async def sensor_history(
    from_time: datetime = Query(..., alias="from"),
    to_time: datetime = Query(..., alias="to"),
    user=Depends(get_current_user),
    db: Session = Depends(db_session),
):
    repo = SensorRepository(db)
    return repo.fetch_by_time(from_time, to_time)
