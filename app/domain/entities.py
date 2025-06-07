from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ClickEvent:
    id: int | None
    url_id: int
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class URL:
    id: int | None
    key: str
    secret_key: str
    target_url: str
    is_active: bool = True
    expires_at: datetime = field(default_factory=datetime.utcnow)
    
    def is_expired(self) -> bool:
        return self.expires_at < datetime.utcnow()

    def deactivate(self):
        self.is_active = False

@dataclass
class URLStats(URL):
    """Сущность для представления статистики"""
    last_hour_clicks: int = 0
    last_day_clicks: int = 0

@dataclass
class User:
    id: int | None
    username: str
    hashed_password: str