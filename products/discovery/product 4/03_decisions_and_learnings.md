# Product 4 — Decisions and Learnings Log

> **Purpose:** Institutional memory. Captures every decision made and lesson learned during the product lifecycle, with reasoning. Prevents re-litigating closed decisions and losing context between sessions.
> **Format:** Reverse chronological. Most recent entries at the top.

---

## July 19, 2026 — Thread opened

### Learnings

---

#### LEARNING 001 — Solution pull is a personal pattern, not a process failure (recurrence)

While closing out the IBOV agent exercise, Raphael sketched a full solution (a GUI with three areas) before any problem isolation had happened. He caught this himself, mid-sketch, and paused before deciding anything.

This is the same pattern already named in `product 3` (see `product 3/03_decisions_and_learnings.md`, LEARNING 001): the impulse to build after seeing a plausible idea, distinct from professional behavior where external accountability provides a natural brake. Seeing it recur across two unrelated products makes it look less like a one-off and more like a default mode to actively design against at the start of every new product thread.

**Practical anchor (carried over from product 3):** Before starting any build, answer: "Would I approve this if I had to justify it to a director with budget at risk?" If no — identify what's missing before proceeding.

---

### Decisions

---

#### DECISION 001 — Open this as a tracked discovery thread, not a build

**Status:** Closed
**Decision:** Log the portfolio/trading app idea as `product 4` under `products/discovery/`, using the same file structure as `product 3`, instead of building or further scoping it inside the IBOV agent exercise conversation.

**Reasoning:** The idea surfaced as a side effect of finishing a Chapter 6 learning exercise, not as a scoped product decision. Giving it its own backlog trail keeps the Chapter 6 exercise scope clean and gives this idea the same discovery discipline `product 3` already went through, instead of it living only inside chat history.
