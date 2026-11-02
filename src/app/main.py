import json
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from . import db, dispatch
from .channels import REGISTRY

app = FastAPI(title="Alerts demo")
db.init()

Category = Literal["news", "market", "disaster"]


class UserIn(BaseModel):
    email: str
    slack_webhook: str | None = None


class RuleIn(BaseModel):
    user_id: int
    category: Category
    min_severity: int = Field(ge=1, le=5)
    channels: list[str] = Field(min_length=1)


class EventIn(BaseModel):
    external_id: str
    category: Category
    severity: int = Field(ge=1, le=5)
    title: str
    body: str = ""


@app.post("/users", status_code=201)
def create_user(u: UserIn):
    with db.conn() as c:
        try:
            cur = c.execute("INSERT INTO users (email, slack_webhook) VALUES (?,?)", (u.email, u.slack_webhook))
        except Exception:
            raise HTTPException(409, "user already exists")
        return {"id": cur.lastrowid}


@app.post("/rules", status_code=201)
def create_rule(r: RuleIn):
    unknown = [ch for ch in r.channels if ch not in REGISTRY]
    if unknown:
        raise HTTPException(422, f"unknown channels: {unknown}. Available: {sorted(REGISTRY)}")
    with db.conn() as c:
        if not c.execute("SELECT 1 FROM users WHERE id = ?", (r.user_id,)).fetchone():
            raise HTTPException(404, "user not found")
        cur = c.execute(
            "INSERT INTO rules (user_id, category, min_severity, channels) VALUES (?,?,?,?)",
            (r.user_id, r.category, r.min_severity, json.dumps(r.channels)),
        )
        return {"id": cur.lastrowid}


@app.post("/events", status_code=202)
def inject_event(e: EventIn):
    event_id, created = dispatch.ingest_event(e.model_dump())
    return {"event_id": event_id, "created": created}


@app.get("/api/admin/{table}")
def admin_list(table: Literal["users", "rules", "events", "deliveries"]):
    with db.conn() as c:
        return [dict(r) for r in c.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT 200")]


@app.post("/api/admin/deliveries/{delivery_id}/retry")
def admin_retry(delivery_id: int):
    if not dispatch.retry(delivery_id):
        raise HTTPException(409, "delivery not found or not in failed state")
    return {"ok": True}


@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return (Path(__file__).parent / "admin.html").read_text(encoding="utf-8")
