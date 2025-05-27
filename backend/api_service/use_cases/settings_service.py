from common.models import GreenhouseSettings
from api_service.interfaces.http.schemas import SettingsOut


class SettingsService:
    def __init__(self, repo):
        self.repo = repo

    def get(self, owner) -> SettingsOut | None:
        row = self.repo.get(owner)  # SQLAlchemy model
        return None if row is None else SettingsOut.from_orm(row)

    def save(self, s: GreenhouseSettings) -> SettingsOut:
        row = self.repo.upsert(s)  # SQLAlchemy model
        return SettingsOut.from_orm(row)
