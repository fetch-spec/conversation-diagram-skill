# Sample conversation (standup — generic)

This file is a **second worked example** so the skill is obviously not
tied to Image Understanding. New conversations should replace this.

---

Standup, 12 Aug.

Alex: checkout API still 504s when inventory is cold. We agreed last week to
put a 2-second cache in front of SKU lookup.

Sam: cache is in review. If it merges today, I'll ship it behind a flag
`CHECKOUT_SKU_CACHE`. Rollback is flip the flag.

Alex: also legal wants a receipt PDF. That's not this week.

Priya: I'll take the 504 on-call until the flag is on. After that, Sam owns
the cache metrics.

Decision: ship cache behind flag this week. Receipt PDF parked.
