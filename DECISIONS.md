# Decision log

| # | Decision | Choice | Why | Rejected |
|---|---|---|---|---|
| 1 | Stack | Python, FastAPI, SQLite | Zero setup for a reviewer, fast to build | Postgres, Node (more setup for no gain here) |
| 2 | Channel extensibility | Abstract `Channel` plus `@register` registry | A new channel touches one file | if/else on channel name |
| 3 | Duplicate protection | `UNIQUE(event_id, rule_id, channel)` on deliveries plus `UNIQUE(external_id)` on events | The database enforces uniqueness, so a repeated event or delivery cannot create a second row, even after a restart. Sequential duplicates are tested. Concurrent duplicates are not. | In-memory "already sent" set |
| 4 | Failure handling | Failures stored with error text, one failing channel never blocks the others, manual retry from admin | Failures are visible to the admin. A crash between inserting a delivery and sending it can leave it stuck as pending (known gap). | Fire-and-forget; auto-retry loop (out of time) |
| 5 | Slack | Incoming webhook per user | No OAuth for a demo | Full Slack app |
| 6 | Email | Console outbox | Real SMTP needs credentials and adds nothing to the design | Faking a "sent" status without a send |
| 7 | Rule creation | Reject unknown channel names up front | A typo should fail loudly, not silently at delivery time | Accepting anything and failing later |
| 8 | Admin UI | One static page, `textContent` only | Event titles are untrusted input. Not yet verified in a browser. | `innerHTML` rendering |
| 9 | Scope | Cut the rule-management UI, auth, queue and real event sources | The task grades process, so the time went into scoping, documentation and checks | Building a full UI and real feeds in one evening |
| 10 | Which build to submit | This FastAPI build | I compared it with a second AI-built version (JavaScript, mock adapters, tests only for matching). This one has tests for duplicates and failed deliveries. | The other build, which has a nicer UI but no tests for those behaviours |
| 11 | Known security and reliability gaps | Documented, not fixed | A rushed fix would be unverified, and a documented gap is more honest than an untested patch | Adding a quick, untested fix |

## Known gaps (accepted, not hidden)
- No auth on the admin page or the API.
- Sending is synchronous inside the request. At volume this needs a queue.
- A user-supplied Slack webhook URL is fetched by the server. A real deployment needs a host allowlist (SSRF risk).
- Retry is manual.
- A delivery can stay `pending` forever if the process crashes before it sends.
- Not tested: severity exactly equal to the threshold, one event matching two rules, concurrent duplicate requests.

## Decision I would revisit first
Synchronous sending. It is the simplest thing that works, but it ties the response time to the slowest channel and is the cause of the pending-after-crash gap.