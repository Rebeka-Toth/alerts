# Architecture

## Overview

```
 Event producers                 Alerts service (FastAPI + SQLite)                 Channels
 (manual inject now,   POST      +-----------+   match   +-----------+   send    +---------+
  feeds/webhooks     /events --> |  events   | --------> |  rules    | --------> | email   |
  later)                         +-----------+           +-----------+     |     +---------+
                                       |                                   +---> | slack   |
                                       v                                   |     +---------+
                                 +------------+   status, error            +---> | future  |
                                 | deliveries | <-------------------------+     +---------+
                                 +------------+
                                       ^
                                       |  read + retry
                                 +------------+
                                 | admin page |
                                 +------------+
```

## Data model (SQLite)

| Table | Purpose | Key constraints |
|---|---|---|
| `users` | Who gets notified; holds an optional Slack webhook | `UNIQUE(email)` |
| `rules` | Category, minimum severity, list of channels | `min_severity` between 1 and 5 |
| `events` | Something that happened, with a source-provided `external_id` | `UNIQUE(external_id)` |
| `deliveries` | One row per (event, rule, channel) with status and error | `UNIQUE(event_id, rule_id, channel)` |

## Flow

1. `POST /events` stores the event. If the `external_id` already exists, nothing else happens (idempotent ingest).
2. `fan_out` selects active rules where the category matches and the event severity is at least the rule's minimum.
3. For each channel in each matching rule, it inserts a `deliveries` row with `INSERT OR IGNORE`. Only a successful insert triggers a send, so the database decides whether a send is a duplicate.
4. `attempt` looks up the channel in the registry, sends, and records `sent` or `failed` with the error text. An exception in one channel is caught per delivery, so other channels are unaffected.
5. The admin page reads the tables through `/api/admin/{table}` and can retry a delivery, which is only allowed while its status is `failed`.

## Extending

- **New channel:** add a `Channel` subclass in `channels.py` with a `name` and `send(user, event)`, decorate it with `@register`. Rule creation validates channel names against the registry, so it becomes available immediately. Matching and dispatch code do not change.
- **New event source:** a producer that calls the same ingest function with a stable `external_id`.
- **New category:** extend the `Category` type in `main.py`.

## Boundaries and known weaknesses

- Sending happens synchronously inside the request. At real volume this belongs in a queue with a worker.
- A user-supplied Slack webhook URL is requested by the server. Production needs a host allowlist (SSRF).
- No authentication on the API or admin page.
- Email is a console outbox.
- Retry is manual and has no backoff.
- If the process dies between inserting a `pending` delivery and sending, that row stays `pending` and is not picked up again. A recovery sweep for stale `pending` rows is the first reliability fix.
