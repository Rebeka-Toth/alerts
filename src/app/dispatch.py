import json
import sqlite3

from . import db
from .channels import REGISTRY


def ingest_event(ev: dict) -> tuple[int, bool]:
    """Store the event and fan out. Returns (event_id, created). Same external_id is a no-op."""
    with db.conn() as c:
        row = c.execute("SELECT id FROM events WHERE external_id = ?", (ev["external_id"],)).fetchone()
        if row:
            return row["id"], False
        try:
            cur = c.execute(
                "INSERT INTO events (external_id, category, severity, title, body) VALUES (?,?,?,?,?)",
                (ev["external_id"], ev["category"], ev["severity"], ev["title"], ev.get("body", "")),
            )
        except sqlite3.IntegrityError:  # concurrent insert of the same external_id
            row = c.execute("SELECT id FROM events WHERE external_id = ?", (ev["external_id"],)).fetchone()
            return row["id"], False
        event_id = cur.lastrowid
    fan_out(event_id)
    return event_id, True


def fan_out(event_id: int) -> None:
    with db.conn() as c:
        event = dict(c.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone())
        rules = c.execute(
            "SELECT * FROM rules WHERE active = 1 AND category = ? AND min_severity <= ?",
            (event["category"], event["severity"]),
        ).fetchall()
        to_send = []
        for rule in rules:
            for ch in json.loads(rule["channels"]):
                # UNIQUE(event_id, rule_id, channel) makes this the duplicate guard, enforced by the DB.
                cur = c.execute(
                    "INSERT OR IGNORE INTO deliveries (event_id, rule_id, channel, status) VALUES (?,?,?, 'pending')",
                    (event_id, rule["id"], ch),
                )
                if cur.rowcount == 1:
                    to_send.append(cur.lastrowid)
    for delivery_id in to_send:
        attempt(delivery_id)


def attempt(delivery_id: int) -> None:
    with db.conn() as c:
        d = c.execute("SELECT * FROM deliveries WHERE id = ?", (delivery_id,)).fetchone()
        event = dict(c.execute("SELECT * FROM events WHERE id = ?", (d["event_id"],)).fetchone())
        rule = c.execute("SELECT * FROM rules WHERE id = ?", (d["rule_id"],)).fetchone()
        user = dict(c.execute("SELECT * FROM users WHERE id = ?", (rule["user_id"],)).fetchone())
    status, error = "sent", None
    try:
        channel = REGISTRY.get(d["channel"])
        if channel is None:
            raise RuntimeError(f"unknown channel '{d['channel']}'")
        channel.send(user, event)
    except Exception as exc:  # one failing channel must not block the others
        status, error = "failed", f"{type(exc).__name__}: {exc}"
    with db.conn() as c:
        c.execute(
            "UPDATE deliveries SET status = ?, error = ?, attempted_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, error, delivery_id),
        )


def retry(delivery_id: int) -> bool:
    with db.conn() as c:
        d = c.execute("SELECT status FROM deliveries WHERE id = ?", (delivery_id,)).fetchone()
    if d is None or d["status"] != "failed":
        return False
    attempt(delivery_id)
    return True
