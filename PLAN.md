# Plan of attack

Timebox: 24 hours. A partial but reasoned slice beats a complete undocumented one.

| Step | Deliverable | Why this order |
|---|---|---|
| 1 | ASSUMPTIONS.md | The brief is ambiguous on purpose. Pinning meaning first stops the AI from inventing it silently. |
| 2 | Data model and channel interface (DECISIONS.md) | Structure decisions come before code so I make them, not the AI. |
| 3 | Thin vertical slice: event in, rule match, channel send, delivery record | Proves the whole path early. |
| 4 | Admin view: rules, events, deliveries, retry | Failures must be visible. |
| 5 | Validation: executable checks plus manual review of AI output | Time reserved so it does not get squeezed. |

## Cut deliberately
Real event sources, auth, async queue, retries with backoff, polished UI.

## Workflow
Prompts are logged in `prompts/`. AI output is treated as a draft: each piece is reviewed against the checks in `notes/VALIDATION.md` before commit.
