from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from app.api.v1.endpoints import urls as urls_v1
from app.api.dependencies import get_url_use_cases
from app.domain.use_cases import URLUseCases


app = FastAPI(
    title="URL Alias Service (Clean Architecture)",
    description="Сервис для сокращения URL, соответствующий тестовому заданию.",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(urls_v1.router, prefix="/api/v1/urls", tags=["URL Management"])


@app.get("/{short_key}", summary="Перенаправление на оригинальный URL", tags=["Public Redirect"])
def forward_to_target_url(
    short_key: str,
    use_cases: URLUseCases = Depends(get_url_use_cases),
):
    url = use_cases.find_and_process_url(short_key)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found, has expired, or is inactive."
        )
    return RedirectResponse(url=url.target_url)