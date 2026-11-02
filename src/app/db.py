import os
import sqlite3
from contextlib import contextmanager

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    slack_webhook TEXT
);
CREATE TABLE IF NOT EXISTS rules (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    category TEXT NOT NULL,
    min_severity INTEGER NOT NULL CHECK (min_severity BETWEEN 1 AND 5),
    channels TEXT NOT NULL,            -- JSON list, e.g. ["email","slack"]
    active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    external_id TEXT NOT NULL UNIQUE,  -- idempotency key from the source
    category TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    title TEXT NOT NULL,
    body TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS deliveries (
    id INTEGER PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id),
    rule_id INTEGER NOT NULL REFERENCES rules(id),
    channel TEXT NOT NULL,
    status TEXT NOT NULL,              -- pending | sent | failed
    error TEXT,
    attempted_at TEXT,
    UNIQUE (event_id, rule_id, channel)
);
"""


def db_path() -> str:
    return os.environ.get("ALERTS_DB", "alerts.db")


@contextmanager
def conn():
    c = sqlite3.connect(db_path())
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init():
    with conn() as c:
        c.executescript(SCHEMA)
