from fastapi.testclient import TestClient
from requests.auth import HTTPBasicAuth


@pytest.fixture(scope="module")
def basic_auth() -> HTTPBasicAuth:
    return HTTPBasicAuth("testuser", "testpassword")


@pytest.fixture(scope="module", autouse=True)
def create_test_user():
    from app.core.security import get_password_hash
    from app.infrastructure.database import SessionLocal, init_db
    from app.infrastructure.models import User
    
    init_db() # Убедимся что таблицы созданы
    db = SessionLocal()
    if not db.query(User).filter(User.username == "testuser").first():
        user = User(username="testuser", hashed_password=get_password_hash("testpassword"))
        db.add(user)
        db.commit()
    db.close()


def test_create_and_redirect(client: TestClient, basic_auth: HTTPBasicAuth):
    # 1. Создание
    response_create = client.post(
        "/api/v1/urls/",
        json={"target_url": "https://www.python.org"},
        auth=basic_auth
    )
    assert response_create.status_code == 201
    data = response_create.json()
    short_key = data["link"].split("/")[-1]
    
    # 2. Редирект
    response_redirect = client.get(f"/{short_key}", allow_redirects=False)
    assert response_redirect.status_code == 307
    assert response_redirect.headers["location"] == "https://www.python.org"


def test_stats_endpoint(client: TestClient, basic_auth: HTTPBasicAuth):
    # 1. Создаем ссылку
    response_create = client.post(
        "/api/v1/urls/",
        json={"target_url": "https://www.djangoproject.com/"},
        auth=basic_auth
    )
    assert response_create.status_code == 201
    data = response_create.json()
    short_key = data["link"].split("/")[-1]

    # 2. Кликаем по ней 3 раза
    for _ in range(3):
        client.get(f"/{short_key}")
    
    # 3. Проверяем статистику
    response_stats = client.get("/api/v1/urls/stats", auth=basic_auth)
    assert response_stats.status_code == 200
    stats_data = response_stats.json()
    
    found_stat = next((s for s in stats_data if s["orig_link"] == "https://www.djangoproject.com/"), None)
    assert found_stat is not None
    assert found_stat["last_hour_clicks"] == 3
    assert found_stat["last_day_clicks"] == 3


def test_unauthorized_access(client: TestClient):
    response = client.post("/api/v1/urls/", json={"target_url": "https://example.com"})
    assert response.status_code == 401