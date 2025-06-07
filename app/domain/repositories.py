from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import URL, User, URLStats


class AbstractURLRepository(ABC):
    @abstractmethod
    def add(self, url: URL) -> URL: ...
    
    @abstractmethod
    def get_by_key(self, key: str) -> Optional[URL]: ...
    
    @abstractmethod
    def get_by_secret_key(self, secret_key: str) -> Optional[URL]: ...
    
    @abstractmethod
    def get_all(self, skip: int, limit: int, active_only: bool) -> List[URL]: ...
    
    @abstractmethod
    def update(self, url: URL) -> URL: ...
    
    @abstractmethod
    def log_click(self, url: URL): ...

    @abstractmethod
    def get_stats(self) -> List[URLStats]: ...


class AbstractUserRepository(ABC):
    @abstractmethod
    def add(self, user: User) -> User: ...

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]: ...