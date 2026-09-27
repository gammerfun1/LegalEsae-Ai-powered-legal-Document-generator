from fastapi.testclient import TestClient

from backend.main import app
from backend import routes


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_validation():
    response = client.post(
        "/generate",
        json={
            "document_type": "",
            "parties": "Alice and Example Corp",
            "terms": "Keep information confidential",
            "dates": "2026-01-01",
        },
    )

    assert response.status_code == 422


def test_generate_success(monkeypatch):

    class FakeGenerator:
        model_name = "test-model"

        def generate_document(self, **kwargs):
            return "TEST DOCUMENT"

    monkeypatch.setattr(
        routes,
        "generator",
        FakeGenerator(),
    )

    response = client.post(
        "/generate",
        json={
            "document_type": "NDA",
            "parties": "Alice and Example Corp",
            "terms": "Keep information confidential",
            "dates": "2026-01-01",
        },
    )

    assert response.status_code == 200
    assert response.json()["content"] == "TEST DOCUMENT"