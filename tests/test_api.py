from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_health_endpoint(monkeypatch):

    from src import api

    monkeypatch.setattr(
        api,
        "check_redis_connection",
        lambda: True
    )

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "api": "healthy",
        "redis": "connected",
        "cache": "available",
        "status": "healthy"
    }
def test_stats_endpoint(monkeypatch):

    from src import api

    expected_stats = {
        "total_queries": 10,
        "cache_hits": 7,
        "cache_misses": 3,
        "hit_rate": 70.0
    }

    monkeypatch.setattr(
        api,
        "get_cache_stats",
        lambda: expected_stats
    )

    response = client.get("/stats")

    assert response.status_code == 200
    assert response.json() == expected_stats

def test_ask_endpoint(monkeypatch):

    from src import api

    monkeypatch.setattr(
        api,
        "ask_question",
        lambda question: "Machine learning is a branch of AI."
    )

    response = client.post(
        "/ask",
        json={"question": "What is machine learning?"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "question": "What is machine learning?",
        "answer": "Machine learning is a branch of AI."
    }

def test_ask_rejects_empty_question():

    response = client.post(
        "/ask",
        json={"question": "   "}
    )

    assert response.status_code == 422