from datetime import datetime, timedelta
import nanoid
from .entities import URL, URLStats
from .repositories import AbstractURLRepository
from ..core.config import settings


class URLUseCases:
    def __init__(self, repo: AbstractURLRepository):
        self.repo = repo

    def _generate_unique_key(self) -> str:
        key = nanoid.generate(size=10)
        while self.repo.get_by_key(key):
            key = nanoid.generate(size=10)
        return key

    def create_url(self, target_url: str) -> URL:
        key = self._generate_unique_key()
        secret_key = f"{key}_{nanoid.generate(size=10)}"
        expires_at = datetime.utcnow() + timedelta(days=settings.DEFAULT_EXPIRATION_DAYS)
        new_url_entity = URL(id=None, target_url=target_url, key=key, secret_key=secret_key, expires_at=expires_at)
        return self.repo.add(new_url_entity)

    def find_and_process_url(self, key: str) -> URL | None:
        url = self.repo.get_by_key(key)
        if not url or not url.is_active or url.is_expired():
            return None
        self.repo.log_click(url)
        return url
        
    def get_all_urls(self, skip: int, limit: int, active_only: bool) -> list[URL]:
        return self.repo.get_all(skip=skip, limit=limit, active_only=active_only)

    def deactivate_url(self, secret_key: str) -> URL | None:
        url = self.repo.get_by_secret_key(secret_key)
        if not url or not url.is_active:
            return None
        url.deactivate()
        return self.repo.update(url)

    def get_url_stats(self) -> list[URLStats]:
        return self.repo.get_stats()