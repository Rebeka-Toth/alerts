# Prompt history

# P1
Prompt:
What should I check to make sure submitting the same event twice doesn't create duplicate events or trigger duplicate notifications? Is an application-level check enough, or should I enforce uniqueness in the database too?

AI said: An application-level check can fail if requests arrive simultaneously. A database-level unique constraint provides an additional safeguard against duplicate events.

How I checked: Read db.py and dispatch.py, then reviewed the duplicate event test in tests/test_checks.py.

What I did: Kept both the database unique constraint and application-level duplicate handling. Concurrent requests are not explicitly tested.




# P2
Prompt:
How should alert rules match incoming events when they have both a category and a minimum severity? Should an event with severity exactly equal to the minimum threshold trigger the rule?

AI said: Both conditions should match, and severity should be greater than or equal to the configured minimum.

How I checked: Read the rule-matching logic in dispatch.py and reviewed the category/severity filtering test in tests/test_checks.py.

What I did: Kept the category and severity filtering logic. The existing test covers matching and non-matching rules.




# P3
Prompt:
If an event triggers both Slack and email notifications, what should happen when Slack fails? How can I prevent one channel's exception from stopping the other deliveries?

AI said: Each notification should be attempted independently, with its own success or failure status. One channel failing should not interrupt the remaining deliveries.

How I checked: Read dispatch.py and channels.py, then reviewed the test simulating Slack failure while email is also configured.

What I did: Kept independent delivery handling and separate delivery status tracking. The test verifies that email can still succeed when Slack fails.




# P4
Prompt:
When retrying failed notifications, how can I make sure successful deliveries aren't sent again? Should I retry the entire event or only the individual failed delivery records?

AI said: Retrying individual failed delivery records is safer than reprocessing the entire event because successful notifications won't need to be sent again.

How I checked: Read the retry implementation in dispatch.py and reviewed the retry test in tests/test_checks.py.

What I did: Kept retry limited to failed deliveries. Automatic retry scheduling is outside the current implementation.




# P5
Prompt:
What should happen if an alert rule references a notification channel that doesn't exist in the channel registry? Should the system silently ignore it or reject it?

AI said: Unknown channels should be rejected explicitly. Silently ignoring them could make a user believe a notification is configured when it will never be delivered.

How I checked: Read the channel registry in channels.py and reviewed the unknown-channel test in tests/test_checks.py.

What I did: Kept explicit rejection of unsupported channel types, rather than silently skipping them..




# P9
Prompt:
I want you to act as an independent senior developer and do a final code review of this project before submission. Go through the codebase and check for bugs, security vulnerabilities, reliability issues, and unnecessary complexity. Run the existing tests and tell me exactly what should be cleaned up or changed, which files are affected, and why. Prioritise important fixes over cosmetic improvements. Don't rewrite the project or add features that are outside the original scope.

AI said: The core implementation and five automated tests were a reasonable MVP, but there were several areas worth reviewing before submission. The main concerns were the lack of authentication on the admin interface, the potential SSRF risk from configurable Slack webhook URLs, synchronous dispatch and uncertain delivery outcomes after a crash, and the absence of real email delivery or automatic retries. It also highlighted that the admin interface and security behaviour needed manual verification.

How I checked: Compared the review findings against `main.py`, `dispatch.py`, `channels.py`, `db.py`, the admin page, the automated tests, and the project documentation. Checked which issues were already documented and which were still limitations. Distinguished actual implementation problems from features outside the MVP scope.

What I did: Kept the existing FastAPI and SQLite architecture rather than rewriting the project. Retained the five automated tests and existing per-channel failure handling and retry logic. Made sure the security and reliability limitations were documented, including missing admin authentication, webhook URL validation/SSRF risk, synchronous dispatch, and uncertain delivery status after a crash. Left production features such as background workers, automatic retries, real email integration, and authentication outside the current scope. Manual browser and security checks remain outstanding.
