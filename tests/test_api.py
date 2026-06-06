import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

load_dotenv()

INDEX_DIR = Path("data/index")

pytestmark = pytest.mark.skipif(
    not INDEX_DIR.exists() or not os.getenv("MISTRAL_API_KEY"),
    reason="Index FAISS ou MISTRAL_API_KEY manquants",
)


@pytest.fixture(scope="module")
def client():
    from src.api.app import app
    with TestClient(app) as c:
        yield c


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_valid_question(client):
    response = client.post("/ask", json={"question": "concerts a Bordeaux"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["answer"], str) and len(data["answer"]) > 0
    assert len(data["sources"]) > 0


def test_ask_empty_question(client):
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422


def test_rebuild_requires_api_key(client):
    response = client.post("/rebuild")
    assert response.status_code == 422  # header manquant


def test_rebuild_rejects_bad_key(client):
    response = client.post("/rebuild", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401