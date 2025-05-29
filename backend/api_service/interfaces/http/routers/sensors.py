from fastapi import APIRouter, Depends
from typing import List
from datetime import datetime

from interfaces.http.schemas import SensorDataCreate, SensorDataRead
from adapters.db.repositories import SensorRepository
from interfaces.http.deps import db_session, get_current_user
from domain.entities import SensorReading

router = APIRouter(prefix="/sensors", tags=["sensors"])

@router.get("/", response_model=List[SensorDataRead])
def read_sensors(skip: int = 0, limit: int = 100,
                 db=Depends(db_session), user=Depends(get_current_user)):
    repo = SensorRepository(db)
    records = repo.fetch_all(skip, limit)
    return [SensorDataRead(**r.__dict__) for r in records]

@router.get("/history", response_model=List[SensorDataRead])
def sensor_history(from_time: datetime, to_time: datetime,
                   db=Depends(db_session), user=Depends(get_current_user)):
    repo = SensorRepository(db)
    records = repo.fetch_by_time(from_time, to_time)
    return [SensorDataRead(**r.__dict__) for r in records]

@router.post("/", response_model=SensorDataRead, status_code=201)
def create_sensor(data: SensorDataCreate,
                  db=Depends(db_session), user=Depends(get_current_user)):
    repo = SensorRepository(db)
    domain = SensorReading(**data.dict())
    saved = repo.insert(domain)
    return SensorDataRead(**saved.__dict__)
