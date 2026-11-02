# Assumptions and open questions

The brief does not define "important", the data source, or how events are detected. For each point below I made an assumption and noted what I would ask the product manager.

## What I assumed
- I assumed an alert fires when an **event** with a category and a severity from 1 to 5 comes in, because the brief never says what "important" means. I picked 1 to 5 as a simple scale. I would ask who assigns severity and whether five levels is enough.
- I assumed three categories (news, market, disaster), taken from the examples in the brief. I would ask whether there are more.
- I assumed a user creates **rules** made of a category, a minimum severity and a list of channels. I would ask whether users also need keyword or region filters.
- I assumed events reach the system through an ingestion endpoint, and that real detection (feeds, price thresholds) would sit in front of it as separate producers. I would ask where the data comes from.
- I assumed every event has an `external_id` from its source, used to avoid duplicates. I would ask whether the sources provide stable ids.
- I assumed one email address and at most one Slack webhook per user. I would ask whether users need several.
- I assumed two identical rules from the same user should produce two notifications, so there is no rule deduplication.
- I assumed the "admin view" means seeing users, rules, events and delivery outcomes, and retrying failed deliveries. I did not model roles, so any admin sees everything.
- I assumed channels share one interface, so adding a new one means adding one class.

## Questions for the PM
1. Who is a "user"? Do we have auth and an existing user table?
2. Who assigns severity, and what does "market movement" mean (percent change, which assets, what window)?
3. Where does news and disaster data come from, and who owns that integration?
4. What volume do we expect? This decides whether sending must move to a queue.
5. Is delivery guaranteed? Is a duplicate worse than a missed alert?
6. Do we need rate limiting or digests for noisy categories?
7. Who is an admin, and may they edit users' rules?

## Explicitly out of scope
Event detection, real feeds, auth, real SMTP, queueing, rate limiting, user-facing UI.