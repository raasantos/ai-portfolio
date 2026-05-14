# Product 3 — Decisions and Learnings Log

> **Purpose:** Institutional memory. Captures every decision made and lesson learned during the product lifecycle, with reasoning. Prevents re-litigating closed decisions and losing context between sessions.
> **Format:** Reverse chronological. Most recent entries at the top.

---

## May 13, 2026 — Problem Discovery Session

### Decisions

---

#### DECISION 001 — Do not build yet

**Status:** Closed
**Decision:** Building is blocked until two prerequisites are met.

**Prerequisites:**
1. Solution scope defined — what exactly the MVP does, for which barrier, at which moment in the user journey
2. Payment mechanic confirmed in the validation experiment — the $100 social campaign must include a real or simulated payment step (paywall, card capture, pre-order), not just signup

**Reasoning:** The pain is validated. Willingness to pay is not. A campaign that measures signups tests interest, not payment intent. Without a payment mechanic, the experiment cannot answer the question it's designed to answer.

**What triggered this:** Recognition of solution pull — the impulse to build before the critical unknown (willingness to pay) is answered. The experiment design ($100 budget + 1-week MVP) is sound in principle but requires tighter mechanics to be valid.

---

#### DECISION 002 — Reject H1, advance H2 with revised framing

**Status:** Closed
**Decision:** H1 ("people don't invest due to lack of knowledge and accessible tools") is rejected. H2 is partially validated and advanced with a revised framing.

**H1 rejection reasoning:**
- Accessible investment platforms already exist in Brazil (NuInvest, Warren, Rico, BTG Digital)
- Financial education content is abundant
- The target segment already uses Nubank — NuInvest is two taps away
- "Tools are missing" is not a defensible claim in 2026

**H2 revised framing:** The barrier is not purely emotional — it is a three-layer barrier:
1. Emotional — fear of loss, anxiety, shame, low confidence
2. Cognitive — perceived complexity, lack of operational knowledge
3. Trust — distrust in banks, advisors, platforms, financial "gurus"

**Why the revision matters:** Calling it purely "emotional" would lead to a solution focused only on reassurance. The cognitive and trust layers require different interventions. Conflating them produces a product that partially solves the problem.

---

#### DECISION 003 — Next step is solution discovery, not user interviews

**Status:** Closed
**Decision:** Skip structured user interviews before the MVP. Replace with a direct solution discovery session followed by a bounded build-and-test experiment.

**Reasoning:** The pain is validated with sufficient confidence across two independent sources and ANBIMA national data. The remaining unknowns (willingness to pay, why existing apps fail for this segment) can be tested more efficiently through a live experiment than through interviews, given the constraints (1-week build, $100 budget, solo execution).

**Condition:** This decision holds only if the MVP scope is defined before building starts. Undefined scope makes "1 week" meaningless.

---

### Learnings

---

#### LEARNING 001 — Solution pull is a personal pattern, not a process failure

The impulse to build after seeing validated pain is a consistent personal pattern, distinct from professional behavior where external accountability provides a natural brake. Named and acknowledged in session.

**Practical anchor:** Before starting any build, answer: "Would I approve this if I had to justify it to a director with budget at risk?" If no — identify what's missing before proceeding.

---

#### LEARNING 002 — The barrier has three layers, not one

Initial framing was "emotional barrier." Research revealed three distinct layers: emotional, cognitive, and trust-based. These are not the same problem and likely require different product interventions.

**Implication for solution discovery:** The MVP must pick one layer to address first. Trying to address all three in a 1-week build produces something shallow that addresses none of them well.

---

#### LEARNING 003 — Willingness to pay is the most critical unvalidated assumption

The research found consistent evidence of pain but zero evidence of payment behavior. The workaround pattern (Reddit, YouTube, free forums) suggests the segment defaults to free solutions. This does not mean they wouldn't pay — it means we don't know yet.

**Implication:** Every experiment until this is answered should include a payment mechanic.

---

#### LEARNING 004 — The segment skews younger than the original hypothesis

The 18–50 age range was observation-based. Reddit data shows 19–25 as the dominant segment in the evidence collected. The 25–50 group is unconfirmed.

**Implication for MVP:** The initial version may need to be calibrated for a narrower segment (19–25, early career, first contact with investing) before expanding.

---

#### LEARNING 005 — The strongest external signal is ANBIMA, not qualitative accounts

Individual Reddit posts and X quotes validate the language and emotional profile. But the ANBIMA data (33% saved in 2025, only 10% invested in financial products, 19% left money completely idle) validates the gap at national scale.

**Implication for positioning:** Any public communication about this product can anchor to a real national data point, not anecdotal evidence.

---

#### LEARNING 006 — Discovery methodology: problem before solution

Early in this session, solution questions were raised before problem validation was complete (what does the agent do? what is the regulatory path?). This was identified and corrected. The sequence — problem hypothesis → research → validation → solution discovery — was followed from that point.

**Repeatable rule:** When a solution question appears during problem discovery, log it as an open question and return to it only after the problem is validated.