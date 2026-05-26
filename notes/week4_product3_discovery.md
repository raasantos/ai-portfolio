# Week 4 — Product 3 Solution Discovery Session

**Date:** May 20, 2026
**Track:** B — Product Build
**Session type:** Solution discovery

---

## What was covered

Full solution discovery cycle for Product 3. Starting from the validated problem (three-layer barrier), this session mapped the user journey, identified the structural gap, derived the product hypothesis, defined the interaction flow, chose the regulatory path, and closed the monetization model.

---

## What was produced

- `products/product3/discovery/04_solution_discovery.md` — complete solution hypothesis
- `products/product3/discovery/01_problem_discovery.md` — updated with user journey map, H3, and revised next steps
- `products/product3/discovery/03_decisions_and_learnings.md` — updated with decisions 004–007 and learnings 007–010
- `notes/week4_produto3_discovery.md` — this file

---

## 10 observations from this session

1. The user journey mapping was the most productive single exercise in both discovery sessions. One diagram from empirical observation produced the core product insight in under 10 minutes — something that research prompts and hours of discussion did not fully surface.

2. The problem is not about knowledge or tools. It is structural: the person who invests had access to a trusted guide. The person who doesn't never did. Same person, different access.

3. The three barrier layers (emotional, cognitive, trust) are not sequential — they are simultaneous and functionally linked. The MVP cannot pick one. It must address all three in a single interaction flow to complete the job.

4. Trust is the gate barrier, but it is not established by the product's features — it is established by what the product explicitly does NOT do. "Não tenho nenhum produto para te vender" is not UX copy. It is the product's core positioning made explicit at the moment it matters most.

5. The trigger question is highly specific: "Você sabe onde posso colocar meu dinheiro em um lugar que rende mais que a poupança?" The product should be designed around this entry point, not around a generic investment education experience.

6. Incumbents (banks, corretoras) have superior data, distribution, and licenses. What they cannot build is credible neutrality. Their revenue model makes the "neutral AI" claim structurally unbelievable regardless of technical reality.

7. "Corretoras could build this" is the exit strategy, not the competitive threat. The path is: validate WTP → build base → negotiate B2B2C from a position of proof.

8. The regulatory path (education framing, not recommendation) is the right call for MVP feasibility. But it introduces the central unvalidated assumption: does understanding options drive action, or does the person still need someone to say "faz isso"?

9. R$20/month as a WTP hypothesis is mathematically defensible but behaviorally unproven. The landing page and campaign must include a real payment mechanic — not just a signup form — to produce a meaningful signal.

10. The MVP has a clear definition of done: a user goes from "onde rende mais que poupança?" to "sei o que fazer e confio na decisão" in a single conversation. If the interaction achieves that, the MVP worked. If the person still hesitates at the end, the education framing failed and the experiment has produced the most important learning possible.

---

## What I still don't understand

- Whether R$20/month is the right price or if it needs A/B testing at R$9.90 and R$29.90
- Which specific investment options to present in the MVP (CDB, LCI/LCA, Tesouro Direto, FIIs — or only the safest subset for this segment?)
- Whether static options or real-time market data changes the trust perception significantly for this segment

---

## How this changes how I think about product

The user journey diagram was more valuable than all the research prompts combined for surfacing the product insight. The insight came from empirical observation of real people — not from data analysis. Data validated the insight. Observation produced it.

This is a useful calibration: research confirms or refutes hypotheses. It does not generate them. The hypothesis generator is proximity to real people with real problems.

The second calibration: "what the product is" and "what the product is not" are equally important decisions. Deciding not to earn commission, deciding not to make explicit recommendations, deciding to declare neutrality upfront — these "not" decisions define the product as much as the feature set.

---

## Open question from this session

Does education framing without explicit recommendation produce action, or does this segment need the equivalent of someone saying "você pode fazer isso, vai dar certo"?

This is not answerable through more discovery. It is only answerable by building and measuring.

---

## Status of week 4 deliverables

| Deliverable | Status |
|---|---|
| products/product3/discovery/04_solution_discovery.md | ✅ Done |
| products/product3/discovery/01_problem_discovery.md (updated) | ✅ Done |
| products/product3/discovery/03_decisions_and_learnings.md (updated) | ✅ Done |
| notes/week4_produto3_discovery.md | ✅ Done |
| notes/week4_function_calling.md | ⚠️ Pending — different session |
| products/career-agent/discovery.md | ⚠️ Pending |
| README do multi-agente | ⚠️ Pending |
| Planilha de vagas (10 entradas) | ⚠️ Pending |
| 3 posts published | ⚠️ In progress |

## Next session — MVP scope and experiment design

Three decisions still needed before build starts:

- [ ] Which investment options does the agent present? (static list definition)
- [ ] Static options or real-time data? (scope decision)
- [ ] Landing page design for the $100 experiment with payment mechanic