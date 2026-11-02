"""Validation checks from notes/VALIDATION.md, as executable tests."""
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("ALERTS_DB", str(tmp_path / "test.db"))
    from app import channels, db
    from app.main import app

    db.init()
    sent = []
    monkeypatch.setattr(channels.EmailChannel, "send", lambda self, user, event: sent.append((user["email"], event["title"])))
    c = TestClient(app)
    c.sent = sent
    return c


def setup_user_with_rule(client, channels, webhook=None, category="disaster", min_sev=3):
    uid = client.post("/users", json={"email": "a@b.hu", "slack_webhook": webhook}).json()["id"]
    client.post("/rules", json={"user_id": uid, "category": category, "min_severity": min_sev, "channels": channels})
    return uid


EVENT = {"external_id": "quake-1", "category": "disaster", "severity": 4, "title": "M6.1 quake"}


def test_same_event_twice_notifies_once(client):
    setup_user_with_rule(client, ["email"])
    r1 = client.post("/events", json=EVENT).json()
    r2 = client.post("/events", json=EVENT).json()
    assert r1["created"] is True and r2["created"] is False
    assert len(client.sent) == 1
    assert len(client.get("/api/admin/deliveries").json()) == 1


def test_below_threshold_and_wrong_category_do_not_notify(client):
    setup_user_with_rule(client, ["email"], min_sev=5)
    client.post("/events", json=EVENT)                                   # severity 4 < 5
    client.post("/events", json={**EVENT, "external_id": "n1", "category": "news", "severity": 5})
    assert client.sent == []


def test_slack_failure_is_recorded_and_email_still_sent(client):
    setup_user_with_rule(client, ["slack", "email"], webhook="http://127.0.0.1:9/nope")
    client.post("/events", json=EVENT)
    rows = {d["channel"]: d for d in client.get("/api/admin/deliveries").json()}
    assert rows["slack"]["status"] == "failed" and rows["slack"]["error"]
    assert rows["email"]["status"] == "sent"
    assert len(client.sent) == 1


def test_retry_only_works_on_failed(client):
    setup_user_with_rule(client, ["slack", "email"], webhook="http://127.0.0.1:9/nope")
    client.post("/events", json=EVENT)
    rows = {d["channel"]: d for d in client.get("/api/admin/deliveries").json()}
    assert client.post(f"/api/admin/deliveries/{rows['email']['id']}/retry").status_code == 409
    assert client.post(f"/api/admin/deliveries/{rows['slack']['id']}/retry").status_code == 200


def test_unknown_channel_rejected_at_rule_creation(client):
    uid = client.post("/users", json={"email": "x@y.hu"}).json()["id"]
    r = client.post("/rules", json={"user_id": uid, "category": "news", "min_severity": 1, "channels": ["sms"]})
    assert r.status_code == 422
