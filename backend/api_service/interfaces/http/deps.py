from fastapi import Depends
from sqlalchemy.orm import Session
from api_service.db import get_db


# Expose database session dependency
def db_session(db: Session = Depends(get_db)) -> Session:
    return db
