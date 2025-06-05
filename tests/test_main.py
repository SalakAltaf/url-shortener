import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Base
from app.database import engine

client = TestClient(app)

# Setup DB for testing - create tables fresh for each test module
@pytest.fixture(scope="module", autouse=True)
def create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_shorten_url():
    response = client.post(
        "/shorten",
        json={"url": "https://test.com"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "code" in data
    assert "short_url" in data
    assert data["short_url"].startswith("http://testserver/")

def test_shorten_url_idempotent():
    url = "https://test.com"
    response1 = client.post("/shorten", json={"url": url})

    print("Response1 status:", response1.status_code)
    print("Response1 JSON:", response1.json())  # <-- Add this line to see the error

    response2 = client.post("/shorten", json={"url": url})

    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response1.json()["code"] == response2.json()["code"]

def test_redirect():
    # Shorten a URL to get a short_code
    response = client.post("/shorten", json={"url": "https://redirect-test.com"})
    assert response.status_code == 201
    short_code = response.json()["code"]

    # Test redirect (do not follow automatically)
    redirect_response = client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_response.status_code in (302, 307)
    assert redirect_response.headers["location"].rstrip("/") == "https://redirect-test.com"

def test_stats_requires_token():
    # Shorten URL to get code
    response = client.post("/shorten", json={"url": "https://stats-test.com"})
    assert response.status_code == 201
    short_code = response.json()["code"]

    # Access stats without token header - should fail (401 or 403)
    response_no_token = client.get(f"/stats/{short_code}")
    assert response_no_token.status_code in (401, 403)

    # Access stats with invalid token - should fail
    response_bad_token = client.get(f"/stats/{short_code}", headers={"token": "bad-token"})
    assert response_bad_token.status_code in (401, 403)

    # Access stats with valid token
    valid_token = "Rawan-711"  # Use your actual valid token here
    response_valid_token = client.get(f"/stats/{short_code}", headers={"token": valid_token})
    assert response_valid_token.status_code == 200
    data = response_valid_token.json()
    assert data["short_code"] == short_code
    assert isinstance(data["clicks"], int)

def test_stats_click_increment():
    # Shorten URL
    response = client.post("/shorten", json={"url": "https://clickcount.com"})
    assert response.status_code == 201
    short_code = response.json()["code"]
    valid_token = "Rawan-711"  # Use your actual valid token here

    # Get initial stats
    response_stats_1 = client.get(f"/stats/{short_code}", headers={"token": valid_token})
    clicks_before = response_stats_1.json()["clicks"]

    # Trigger redirect (simulate a click)
    client.get(f"/{short_code}", follow_redirects=False)

    # Get stats after redirect
    response_stats_2 = client.get(f"/stats/{short_code}", headers={"token": valid_token})
    clicks_after = response_stats_2.json()["clicks"]

    assert clicks_after == clicks_before + 1

