from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from app.api.v1 import schemas
from app.api.dependencies import get_url_use_cases, get_current_user
from app.domain.use_cases import URLUseCases

router = APIRouter()

@router.post(
    "/",
    response_model=schemas.URLInfo,
    status_code=status.HTTP_201_CREATED,
    summary="Создание короткой ссылки",
    dependencies=[Depends(get_current_user)]
)
def create_url(request: Request, payload: schemas.URLCreate, use_cases: URLUseCases = Depends(get_url_use_cases)):
    url = use_cases.create_url(target_url=str(payload.target_url))
    base_url = str(request.base_url).rstrip('/')
    return schemas.URLInfo(
        link=f"{base_url}/{url.key}",
        orig_link=url.target_url,
        secret_key=url.secret_key,
    )

@router.get(
    "/",
    response_model=list[schemas.URLDetails],
    summary="Получение списка всех ссылок",
    dependencies=[Depends(get_current_user)]
)
def read_urls(
    request: Request,
    skip: int = Query(0, ge=0, description="Смещение для пагинации"),
    limit: int = Query(100, ge=1, le=200, description="Количество записей на странице"),
    active_only: bool = Query(False, description="Фильтровать только по активным ссылкам"),
    use_cases: URLUseCases = Depends(get_url_use_cases)
):
    urls = use_cases.get_all_urls(skip=skip, limit=limit, active_only=active_only)
    base_url = str(request.base_url).rstrip('/')
    return [
        schemas.URLDetails(
            link=f"{base_url}/{url.key}",
            orig_link=url.target_url,
            is_active=url.is_active,
            expires_at=url.expires_at
        ) for url in urls
    ]

@router.delete(
    "/{secret_key}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Деактивация ссылки",
    dependencies=[Depends(get_current_user)]
)
def deactivate_url(secret_key: str, use_cases: URLUseCases = Depends(get_url_use_cases)):
    url = use_cases.deactivate_url(secret_key)
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found or already inactive")
    return None

@router.get("/stats", response_model=list[schemas.URLStatsResponse], summary="Получение статистики по переходам", dependencies=[Depends(get_current_user)])
def get_stats(request: Request, use_cases: URLUseCases = Depends(get_url_use_cases)):
    stats = use_cases.get_url_stats()
    base_url = str(request.base_url).rstrip('/')
    return [
        schemas.URLStatsResponse(
            link=f"{base_url}/{stat.key}",
            orig_link=stat.target_url,
            last_hour_clicks=stat.last_hour_clicks,
            last_day_clicks=stat.last_day_clicks,
        ) for stat in stats
    ]