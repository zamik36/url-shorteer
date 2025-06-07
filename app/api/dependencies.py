from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from app.domain.entities import User as UserEntity
from app.domain.use_cases import URLUseCases
from app.domain.repositories import AbstractURLRepository, AbstractUserRepository
from app.infrastructure.database import SessionLocal
from app.infrastructure.repositories.postgres import PostgresURLRepository, PostgresUserRepository
from app.core.auth import verify_password

security = HTTPBasic()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_url_repo(db: Session = Depends(get_db)) -> AbstractURLRepository:
    return PostgresURLRepository(db)


def get_user_repo(db: Session = Depends(get_db)) -> AbstractUserRepository:
    return PostgresUserRepository(db)


def get_url_use_cases(repo: AbstractURLRepository = Depends(get_url_repo)) -> URLUseCases:
    return URLUseCases(repo)


def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
    repo: AbstractUserRepository = Depends(get_user_repo)
) -> UserEntity:
    user = repo.get_by_username(credentials.username)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user