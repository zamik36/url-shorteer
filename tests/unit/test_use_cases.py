import pytest
from app.domain.entities import URL, URLStats
from app.domain.use_cases import URLUseCases
from app.domain.repositories import AbstractURLRepository

class InMemoryURLRepository(AbstractURLRepository):
    """Фейковый репозиторий для unit-тестов."""
    def __init__(self):
        self._data: dict[str, URL] = {}
        self._secrets: dict[str, URL] = {}
        self._clicks: list[tuple[int, object]] = []
        self._next_id = 1

    def add(self, url: URL) -> URL:
        url.id = self._next_id
        self._data[url.key] = url
        self._secrets[url.secret_key] = url
        self._next_id += 1
        return url
    
    def get_by_key(self, key: str) -> URL | None: return self._data.get(key)
    def get_by_secret_key(self, key: str) -> URL | None: return self._secrets.get(key)
    def get_all(self, skip, limit, active_only): return list(self._data.values())[skip:skip+limit]
    def update(self, url: URL) -> URL: self._data[url.key] = url; return url
    def log_click(self, url: URL): self._clicks.append((url.id, object()))
    def get_stats(self) -> list[URLStats]: return [] # Для unit-тестов это не так важно

@pytest.fixture
def url_use_cases() -> URLUseCases:
    return URLUseCases(repo=InMemoryURLRepository())

def test_create_url(url_use_cases: URLUseCases):
    target_url = "https://example.com"
    result = url_use_cases.create_url(target_url)
    assert result.target_url == target_url
    assert url_use_cases.repo.get_by_key(result.key) is not None

def test_find_and_process_url_logs_click(url_use_cases: URLUseCases):
    created_url = url_use_cases.create_url("https://test.com")
    assert len(url_use_cases.repo._clicks) == 0
    
    url_use_cases.find_and_process_url(created_url.key)
    assert len(url_use_cases.repo._clicks) == 1

def test_deactivate_url(url_use_cases: URLUseCases):
    url = url_use_cases.create_url("https://test.com")
    assert url.is_active is True
    
    deactivated_url = url_use_cases.deactivate_url(url.secret_key)
    assert deactivated_url.is_active is False
    assert url_use_cases.find_and_process_url(url.key) is None