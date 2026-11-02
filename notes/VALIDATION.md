# Validation log

Checks run against AI-generated code.

Automated: `pytest` (tests/test_checks.py). Run in the AI sandbox: 5 passed. Local rerun still outstanding.

| # | Check | How | Result | What I did |
|---|---|---|---|---|
| 1 | Same event posted twice notifies once | `test_same_event_twice_notifies_once` | PASS (sandbox) | Confirmed the automated test passed. Local rerun not yet performed. |
| 2 | Below-threshold or wrong-category events do not notify | `test_below_threshold_and_wrong_category_do_not_notify` | PASS (sandbox) | Confirmed the automated test passed. Local rerun not yet performed. |
| 3 | Slack failure is recorded and email still sends | `test_slack_failure_is_recorded_and_email_still_sent` | PASS (sandbox) | Confirmed the automated test passed. Local rerun not yet performed. |
| 4 | Retry only allowed on failed deliveries | `test_retry_only_works_on_failed` | PASS (sandbox) | Confirmed the automated test passed. Local rerun not yet performed. |
| 5 | Unknown channel rejected at rule creation | `test_unknown_channel_rejected_at_rule_creation` | PASS (sandbox) | Confirmed the automated test passed. Local rerun not yet performed. |
| 6 | No secrets or webhook URLs hardcoded | `grep -rn "hooks.slack" src/` | NOT VERIFIED | Source reviewed, but the grep command has not been run and recorded. |
| 7 | Admin page shows real DB rows, not sample data | Open `/admin` after the README demo | NOT VERIFIED | Admin implementation reviewed; browser check against a running local database is still outstanding. |
| 8 | Admin cannot be XSSed by an event title | Post an event titled `<img src=x onerror=alert(1)>`, open `/admin` | NOT VERIFIED | Dynamic admin values appear to use `textContent`; the manual browser test has not been performed. |

Checks 6 to 8 were not run because of time

## Things reviewed in the AI draft

- Initial idea of an in-memory dedupe set: rejected, moved to DB constraints (decision 3).
- Per-channel delivery failures are isolated, so a Slack failure does not block an email attempt.
- Retry logic targets failed deliveries rather than resending successful ones.
- Admin page uses `textContent` for dynamic values, reducing the risk of event-title HTML being executed. Manual XSS verification remains outstanding.
- Slack webhook configuration is a security concern: user-controlled destinations need URL validation and network restrictions to mitigate SSRF.
- Synchronous dispatch has a reliability limitation: a crash between sending a notification and recording its status can leave the delivery outcome uncertain.
- No authentication is implemented for the admin interface; it should not be exposed publicly as-is.

