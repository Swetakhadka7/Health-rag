import pytest
from fastapi.testclient import TestClient

import api

KEY = "test-key"
GOOD = {"X-API-Key": KEY}
BODY = {"question": "Can I give ibuprofen to a child with dengue fever?"}
REFUSAL = "I can't answer this from the documents I have."


def fake_answer(question):
    return "No NSAIDs [1].", [{"n": 1, "doc": "d.pdf", "page": 3}], []


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("API_KEY", KEY)
    api._hits.clear()
    monkeypatch.setattr(api, "answer", fake_answer)
    with TestClient(api.app) as c:
        yield c


def test_health_is_open(client):
    assert client.get("/health").status_code == 200


def test_missing_key_is_rejected(client):
    assert client.post("/ask", json=BODY).status_code == 401


def test_wrong_key_is_rejected(client):
    r = client.post("/ask", json=BODY, headers={"X-API-Key": "nope"})
    assert r.status_code == 401


def test_valid_key_returns_cited_answer(client):
    r = client.post("/ask", json=BODY, headers=GOOD)
    assert r.status_code == 200
    data = r.json()
    assert data["answer"] == "No NSAIDs [1]."
    assert data["refused"] is False
    assert data["sources"] == [{"n": 1, "doc": "d.pdf", "page": 3}]


def test_refusal_is_flagged(client, monkeypatch):
    monkeypatch.setattr(api, "answer", lambda q: (REFUSAL, [], []))
    data = client.post("/ask", json=BODY, headers=GOOD).json()
    assert data["refused"] is True
    assert data["sources"] == []


def test_short_question_is_rejected(client):
    r = client.post("/ask", json={"question": "hi"}, headers=GOOD)
    assert r.status_code == 422


def test_too_many_requests_get_429(client, monkeypatch):
    monkeypatch.setattr(api, "RATE_LIMIT", 3)
    codes = [client.post("/ask", json=BODY, headers=GOOD).status_code for _ in range(4)]
    assert codes == [200, 200, 200, 429]
    r = client.post("/ask", json=BODY, headers=GOOD)
    assert int(r.headers["retry-after"]) > 0


def test_wrong_keys_do_not_use_up_the_limit(client, monkeypatch):
    monkeypatch.setattr(api, "RATE_LIMIT", 3)
    for _ in range(5):
        client.post("/ask", json=BODY, headers={"X-API-Key": "nope"})
    assert client.post("/ask", json=BODY, headers=GOOD).status_code == 200


def test_language_model_down_gives_503(client, monkeypatch):
    monkeypatch.setattr(api, "answer", lambda q: (None, [], []))
    assert client.post("/ask", json=BODY, headers=GOOD).status_code == 503


def test_server_refuses_to_start_without_api_key(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        with TestClient(api.app):
            pass