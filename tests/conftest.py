import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import storage


@pytest.fixture(autouse=True)
def clear_storage() -> None:
    storage.reset()
    yield
    storage.reset()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
