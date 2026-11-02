# Retrospective

## What this submission demonstrates

The brief left "important", the data source and the detection method undefined. I did not invent a detector. I narrowed the problem to a pipeline whose guarantees can be tested: an event with a category and severity comes in, matching rules are selected, each selected channel gets exactly one delivery attempt, and the outcome is recorded and visible to an admin.

The design choices that carry the most weight are the database constraints for duplicate protection, per-delivery failure isolation, and a channel registry that validates rules at creation. Each is covered by an automated test (`tests/test_checks.py`).

## What was deliberately cut

Real event sources, a user-facing UI for managing rules, authentication, a queue, automatic retries and real email sending. The scope was time-boxed to one day, so I put the time into scoping documents and checks rather than breadth.

## What remains unresolved (needs the product owner)

- What counts as important, per category (severity scale, thresholds, market definition).
- Who the users are and who the admins are.
- Whether a missed alert or a duplicate alert is worse, which decides at-least-once versus at-most-once delivery.
- Volume, rate limiting and digesting.
- Data retention for events and delivery logs.

## Known gap in the demo

Creating users and rules is done through the API. The admin page is read-and-retry only. A form for rule management is the most visible missing piece.

## Next steps with more time

1. Rule-management UI and per-user views.
2. Move sending to a queue with a worker, exponential backoff and a sweep for stale `pending` deliveries.
3. Allowlist Slack webhook hosts and store credentials server-side.
4. Real email provider behind the same `Channel` interface.
5. Real event producers (for example an earthquake feed) that map into the ingest function with stable ids.
6. Authentication, roles and an audit trail on admin actions.

## My review of the AI output

- Rejected: in-memory "already sent" set for duplicates, replaced by database constraints.
- Accepted with limitations: the AI's per-channel failure handling and manual retry approach. I checked the dispatch logic and the corresponding tests.
- Identified as unresolved: the Slack webhook implementation accepts a configurable URL without sufficient destination restrictions. I documented the SSRF risk instead of treating the demo as production-ready. I also noted that synchronous dispatch can leave deliveries stuck in `pending` if the application crashes. 
