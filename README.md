# Alerts: from vague brief to working slice

Process-first submission. Read in this order: `ASSUMPTIONS.md`, `PLAN.md`, `DECISIONS.md`, `docs/ARCHITECTURE.md`, `notes/VALIDATION.md`, `docs/RETROSPECTIVE.md`, then the code.

## Run it
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd src && uvicorn app.main:app --reload     # admin: http://127.0.0.1:8000/admin
pytest                                       # from repo root: runs the validation checks
```

## Demo
```
curl -XPOST localhost:8000/users  -H 'content-type: application/json' -d '{"email":"me@example.com"}'
curl -XPOST localhost:8000/rules  -H 'content-type: application/json' -d '{"user_id":1,"category":"disaster","min_severity":3,"channels":["email","slack"]}'
curl -XPOST localhost:8000/events -H 'content-type: application/json' -d '{"external_id":"q1","category":"disaster","severity":4,"title":"M6.1 earthquake"}'
```
Email prints to the console. Slack fails visibly (no webhook), which shows up in the admin view with a Retry button.

## Scope honesty
Event detection, real event sources, auth and a real email sender are deliberately out of scope. See `ASSUMPTIONS.md`.
