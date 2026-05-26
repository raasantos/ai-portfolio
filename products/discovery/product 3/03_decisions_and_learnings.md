# Product 3 — Decisions and Learnings Log

> **Purpose:** Institutional memory. Captures every decision made and lesson learned during the product lifecycle, with reasoning. Prevents re-litigating closed decisions and losing context between sessions.
> **Format:** Reverse chronological. Most recent entries at the top.

---

## May 20, 2026 — Solution Discovery Session

### Decisions

---

#### DECISION 007 — Education framing is the regulatory path for the MVP

**Status:** Closed
**Decision:** The MVP will present investment options and explain risks without making explicit personalized recommendations ("you should invest in X"). The user makes the final decision.

**Reasoning:**
- Explicit personalized investment recommendation requires CVM registration (Resolution 30, Instruction 539) or partnership with a licensed institution
- Education framing is executable within MVP constraints (1-week build, solo)
- Preserves the exit option: validate first, negotiate corretora partnership after traction is proven

**Risk acknowledged:** Education framing may not be sufficient to drive action. Some users may need an explicit recommendation to take the final step. This is the central learning the MVP must answer.

**Condition:** If experiment shows education framing fails to drive action, two paths open: pursue corretora partnership before scaling, or redesign the minimum interaction that drives action within education framing.

---

#### DECISION 006 — Incumbents cannot credibly copy the trust positioning

**Status:** Closed
**Decision:** The primary competitive moat is trust positioning — "no financial interest in what you choose" — which a bank-owned or corretora-owned product cannot credibly claim regardless of technical capability.

**Reasoning:** The target segment's distrust is directed at institutions, not at technology. A bank launching "our neutral AI" is not believable when their revenue depends on product distribution. An independent product can own this positioning in a way an institution cannot.

**Strategic implication:** "Corretoras could build this" is the exit path, not the threat. Validate → build user base with confirmed WTP → negotiate B2B2C with corretora from a position of proof.

---

#### DECISION 005 — Trust declaration is a mandatory product element, not optional UX

**Status:** Closed
**Decision:** The agent must establish neutrality explicitly at the start of every interaction before asking profile questions.

**Required declaration (or equivalent):** "Não tenho nenhum produto para te vender e não ganho nada dependendo do que você escolher. Meu trabalho é só te ajudar a entender suas opções."

**Reasoning:** The user journey map shows the segment arrives with active distrust of advisors and bank managers. Without establishing neutrality upfront, the agent is perceived as another product selling something — which collapses the core differentiator before it can work.

---

#### DECISION 004 — Monetization model is monthly subscription at R$20/month (hypothesis)

**Status:** Closed — hypothesis, not validated
**Decision:** The product will charge a monthly subscription. WTP hypothesis: R$20/month.

**Reasoning:**
- Commission model replicates the conflict of interest that makes banks untrustworthy — incompatible with the core positioning
- R$20/month is defensible on paper: a user with R$20k migrating from poupança to CDB at 12% CDI gains ~R$2,400/year, making the R$240/year subscription cost ROI-positive within year one
- R$20/month is the hypothesis to test, not the final price — experiment may surface a different price point

**What must be tested:** Whether users in this income segment perceive the value as worth R$20/month before experiencing the product. The landing page and campaign must include a real payment mechanic to measure this.

---

### Learnings

---

#### LEARNING 010 — The three-layer barrier is addressed together, not sequentially

Initial assumption was that the MVP should pick one barrier layer to attack first. Solution discovery revealed the three layers are functionally linked in the user journey — profile assessment addresses cognitive, risk explanation addresses emotional, trust declaration addresses trust. Separating them produces a product that feels incomplete.

**Revised implication:** The MVP minimum is the full interaction flow (profile → options with risk → guided action), not a single layer in isolation.

---

#### LEARNING 009 — Education framing without explicit recommendation may not drive action

The regulatory path chosen (education, not recommendation) preserves MVP feasibility but introduces an untested assumption: that understanding options is sufficient for someone to make a decision. The user journey map shows the success path includes "espera confirmação e validação" — the person waits for someone to confirm they are on the right path.

If education framing fails to provide that confirmation moment, the product solves the informational problem but not the behavioral one.

**This is the central learning the MVP exists to answer.**

---

#### LEARNING 008 — The trigger question defines the product entry point

The user journey mapping revealed a specific trigger question that appears consistently: *"Você sabe onde posso colocar meu dinheiro em um lugar que rende mais que a poupança?"*

This is not "teach me about investing." It is one specific, low-stakes question to a trusted person. The product should be designed around this exact entry point — not a generic "how can I help you?" but a direct response to this specific moment of intent.

**Implication for design:** The landing page, the onboarding, and the first interaction should speak directly to this question.

---

#### LEARNING 007 — The gap is not about tools — it is about access to a trusted guide

The user journey mapping confirmed that the problem is structural, not informational. The same person either invests or does not, depending on whether they have access to someone trustworthy to walk them through the decision.

The guide that exists for this segment (bank manager) is inaccessible for the purpose of trust because of conflict of interest. The trustworthy guide (independent advisor) is inaccessible because of economics.

**The product is not a tool. It is a substitute for the trusted person this segment has never had access to.**

---

## May 13, 2026 — Problem Discovery Session

### Decisions

---

#### DECISION 003 — Next step is solution discovery, not user interviews

**Status:** Closed
**Decision:** Skip structured user interviews before the MVP. Replace with a direct solution discovery session followed by a bounded build-and-test experiment.

**Reasoning:** The pain is validated with sufficient confidence across two independent sources and ANBIMA national data. The remaining unknowns (willingness to pay, why existing apps fail for this segment) can be tested more efficiently through a live experiment than through interviews, given the constraints (1-week build, $100 budget, solo execution).

**Condition:** This decision holds only if the MVP scope is defined before building starts. Undefined scope makes "1 week" meaningless.

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

#### DECISION 001 — Do not build yet

**Status:** Closed — prerequisites now met as of May 20, 2026
**Decision:** Building was blocked until two prerequisites were met.

**Prerequisites:**
1. Solution scope defined ✅ — completed May 20, 2026
2. Payment mechanic confirmed in the validation experiment — the $100 social campaign must include a real or simulated payment step (paywall, card capture, pre-order), not just signup

**Status of prerequisite 2:** Still pending — experiment design not yet complete.

---

### Learnings

---

#### LEARNING 006 — Discovery methodology: problem before solution

Early in this session, solution questions were raised before problem validation was complete (what does the agent do? what is the regulatory path?). This was identified and corrected. The sequence — problem hypothesis → research → validation → solution discovery — was followed from that point.

**Repeatable rule:** When a solution question appears during problem discovery, log it as an open question and return to it only after the problem is validated.

---

#### LEARNING 005 — The strongest external signal is ANBIMA, not qualitative accounts

Individual Reddit posts and X quotes validate the language and emotional profile. But the ANBIMA data (33% saved in 2025, only 10% invested in financial products, 19% left money completely idle) validates the gap at national scale.

**Implication for positioning:** Any public communication about this product can anchor to a real national data point, not anecdotal evidence.

---

#### LEARNING 004 — The segment skews younger than the original hypothesis

The 18–50 age range was observation-based. Reddit data shows 19–25 as the dominant segment in the evidence collected. The 25–50 group is unconfirmed.

**Implication for MVP:** The initial version may need to be calibrated for a narrower segment (19–25, early career, first contact with investing) before expanding.

---

#### LEARNING 003 — Willingness to pay is the most critical unvalidated assumption

The research found consistent evidence of pain but zero evidence of payment behavior. The workaround pattern (Reddit, YouTube, free forums) suggests the segment defaults to free solutions. This does not mean they wouldn't pay — it means we don't know yet.

**Implication:** Every experiment until this is answered should include a payment mechanic.

---

#### LEARNING 002 — The barrier has three layers, not one

Initial framing was "emotional barrier." Research revealed three distinct layers: emotional, cognitive, and trust-based. These are not the same problem and likely require different product interventions.

**Revised implication (May 20):** The three layers are functionally linked in the user journey and must be addressed together in the MVP interaction flow, not sequentially.

---

#### LEARNING 001 — Solution pull is a personal pattern, not a process failure

The impulse to build after seeing validated pain is a consistent personal pattern, distinct from professional behavior where external accountability provides a natural brake. Named and acknowledged in session.

**Practical anchor:** Before starting any build, answer: "Would I approve this if I had to justify it to a director with budget at risk?" If no — identify what's missing before proceeding.