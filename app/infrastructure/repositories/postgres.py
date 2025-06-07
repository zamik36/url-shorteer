from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.domain.entities import URL as URLEntity, User as UserEntity, URLStats
from app.domain.repositories import AbstractURLRepository, AbstractUserRepository
from .. import models


class PostgresURLRepository(AbstractURLRepository):
    def __init__(self, session: Session):
        self.db = session

    def _to_entity(self, db_url: models.URL) -> URLEntity:
        return URLEntity(
            id=db_url.id, key=db_url.key, secret_key=db_url.secret_key,
            target_url=db_url.target_url, is_active=db_url.is_active,
            expires_at=db_url.expires_at,
        )

    def add(self, url: URLEntity) -> URLEntity:
        db_url = models.URL(key=url.key, secret_key=url.secret_key, target_url=url.target_url, is_active=url.is_active, expires_at=url.expires_at)
        self.db.add(db_url)
        self.db.commit()
        self.db.refresh(db_url)
        return self._to_entity(db_url)

    def get_by_key(self, key: str) -> Optional[URLEntity]:
        db_url = self.db.query(models.URL).filter(models.URL.key == key).first()
        return self._to_entity(db_url) if db_url else None
    
    def get_by_secret_key(self, secret_key: str) -> Optional[URLEntity]:
        db_url = self.db.query(models.URL).filter(models.URL.secret_key == secret_key).first()
        return self._to_entity(db_url) if db_url else None
        
    def get_all(self, skip: int, limit: int, active_only: bool) -> List[URLEntity]:
        query = self.db.query(models.URL)
        if active_only:
            query = query.filter(models.URL.is_active == True, models.URL.expires_at > datetime.utcnow())
        db_urls = query.order_by(models.URL.id.desc()).offset(skip).limit(limit).all()
        return [self._to_entity(url) for url in db_urls]

    def update(self, url: URLEntity) -> URLEntity:
        db_url = self.db.get(models.URL, url.id)
        if db_url:
            db_url.is_active = url.is_active
            self.db.commit()
            self.db.refresh(db_url)
            return self._to_entity(db_url)
        raise ValueError("URL not found for update")
        
    def log_click(self, url: URLEntity):
        click = models.ClickEvent(url_id=url.id)
        self.db.add(click)
        self.db.commit()

    def get_stats(self) -> List[URLStats]:
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)

        clicks_subquery = (
            self.db.query(
                models.ClickEvent.url_id,
                func.count(models.ClickEvent.id).label("total_clicks"),
                func.count(case((models.ClickEvent.timestamp >= one_hour_ago, 1))).label("last_hour_clicks"),
                func.count(case((models.ClickEvent.timestamp >= one_day_ago, 1))).label("last_day_clicks"),
            ).group_by(models.ClickEvent.url_id).subquery()
        )

        results = (
            self.db.query(
                models.URL,
                func.coalesce(clicks_subquery.c.last_hour_clicks, 0).label("lh_clicks"),
                func.coalesce(clicks_subquery.c.last_day_clicks, 0).label("ld_clicks"),
            ).outerjoin(clicks_subquery, models.URL.id == clicks_subquery.c.url_id)
            .order_by(func.coalesce(clicks_subquery.c.total_clicks, 0).desc())
            .all()
        )

        return [
            URLStats(
                id=url.id, key=url.key, secret_key=url.secret_key, target_url=url.target_url,
                is_active=url.is_active, expires_at=url.expires_at,
                last_hour_clicks=lh_clicks, last_day_clicks=ld_clicks
            ) for url, lh_clicks, ld_clicks in results
        ]


class PostgresUserRepository(AbstractUserRepository):
    def __init__(self, session: Session):
        self.db = session

    def add(self, user: UserEntity) -> UserEntity:
        db_user = models.User(username=user.username, hashed_password=user.hashed_password)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        user.id = db_user.id
        return user

    def get_by_username(self, username: str) -> Optional[UserEntity]:
        db_user = self.db.query(models.User).filter(models.User.username == username).first()
        if db_user:
            return UserEntity(
                id=db_user.id, username=db_user.username,
                hashed_password=db_user.hashed_password
            )
        return None