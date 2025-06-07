from domain.entities import GreenhouseSettings
from adapters.db.repositories import SettingsRepository

class SettingsService:
    def __init__(self, repo: SettingsRepository):
        self.repo = repo

    def get(self, owner: str) -> GreenhouseSettings | None:
        return self.repo.get(owner)

    def save(self, gh: GreenhouseSettings) -> GreenhouseSettings:
        return self.repo.upsert(gh)
