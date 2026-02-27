from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_events_list_validation():
    response = client.get("/events", params={"limit": 1000})
    assert response.status_code == 422


def test_alerts_list_endpoint(monkeypatch):
    from app.api import alerts

    monkeypatch.setattr(alerts.service, "list_rules", lambda db: [])
    response = client.get("/alerts")
    assert response.status_code == 200
    assert response.json() == []


def test_analytics_summary(monkeypatch):
    from app.api import analytics

    monkeypatch.setattr(
        analytics.service,
        "summary",
        lambda db: {"total_events": 10, "total_alerts": 2, "latest_event_timestamp": datetime.now(timezone.utc).isoformat()},
    )
    response = client.get("/analytics/summary")
    assert response.status_code == 200
    assert response.json()["total_events"] == 10


def test_internal_ingest_unauthorized():
    response = client.post(
        "/internal/events",
        json={
            "event_id": str(uuid4()),
            "source_id": "source-1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": "high",
            "event_type": "cpu_spike",
            "payload": {"value": 90},
        },
        headers={"x-ingest-token": "bad"},
    )
    assert response.status_code == 401
