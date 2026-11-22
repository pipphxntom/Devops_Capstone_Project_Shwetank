import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))

from main import app, init_db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    os.environ["DATABASE_PATH"] = ":memory:"
    init_db()
    with app.test_client() as c:
        yield c

def test_dashboard_loads(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"FlowForge" in r.data

def test_liveness(client):
    r = client.get("/health/live")
    assert r.status_code == 200
    assert r.get_json()["status"] == "up"

def test_readiness(client):
    r = client.get("/health/ready")
    assert r.status_code == 200
    body = r.get_json()
    assert body["status"] == "ready"
    assert body["db"] == "ok"

def test_create_and_list_incident(client):
    post = client.post("/api/v1/incidents", json={"title": "Blue-green cutover", "severity": "high"})
    assert post.status_code == 201

    get = client.get("/api/v1/incidents")
    assert get.status_code == 200
    data = get.get_json()
    assert data["count"] >= 1
    assert any(i["title"] == "Blue-green cutover" for i in data["incidents"])

def test_metrics(client):
    r = client.get("/metrics")
    assert r.status_code == 200
    assert b"flowforge_http_requests_total" in r.data
