import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home_path(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"URLs shortener" in response.data
