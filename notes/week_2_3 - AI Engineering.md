# Week 2-3 — AI Engineering: Chapters 2 and 3

**Date:** May 5–19, 2026
**Chapters covered:** Chapter 2 (How Foundation Models Work) + Chapter 3 (Evaluation — Methods)

---

## 10 observations I made (not a summary — what caught my attention)

1. **Pre-training and post-training are phases with completely different goals.** Pre-training defines what the model knows. Post-training defines how it behaves. As a PM, almost everything that matters for the product lives in post-training — that's where prompt engineering and finetuning operate.

2. **Temperature is a product decision, not an engineering one.** The PM defines whether the product needs precision or creativity. Engineering implements. Leaving this decision to engineering means abdicating a variable that directly impacts user experience.

3. **Hallucination is not a bug — it's a structural property.** The model doesn't differentiate between data it received and data it generated. This won't be "fixed" — it will be managed. A PM needs to map where the product tolerates it and where it doesn't, and design safeguards proportional to the risk.

4. **Eval is a business cost, not technical overhead.** Before including any AI feature in a product, the cost of eval needs to be in the business model. A product without eval is operating with invisible risk — not zero risk.

5. **Quality threshold is a product decision.** There is no "technically correct" threshold. The question is: what is the expected value of the error compared to the cost of preventing it? In some contexts, accepting calculated risk and paying a fine has positive expected value. The difference between that and negligence is that the risk was mapped and formally accepted.

6. **No single eval method covers all angles.** Each method has blind spots. Combining methods is not a fallback — it's standard practice. The right combination depends on the product's risk profile.

7. **AI-as-judge has three specific biases that contaminate evaluation data:** self-preference (favors its own style), verbosity (favors longer responses), and position (favors first or last response when comparing two). Decisions based on this data without accounting for these biases are distorted decisions.

8. **Embedding is a product design decision disguised as a technical one.** When you choose an embedding model, you're defining what the product understands as "relevant" and "similar." Changing this decision later invalidates all stored vectors — high reprocessing cost.

9. **The real quality signal is not a thumbs up — it's user action.** A response that generated behavior (applied for a job, published a post, made a decision) is worth more than a well-rated response. Optimizing for immediate satisfaction ≠ optimizing for real outcomes.

10. **I arrived at the AI-as-judge concept empirically before knowing the name.** I've been using this method for 6+ months to evaluate meetings, documents, product artifacts, decisions, and writing. This confirms that applied product reasoning arrives at the same structures the literature names — the difference is formalization.

---

## What I still don't understand

- How to build a systematic eval pipeline (Chapter 4 should answer this)
- How to version evaluation prompts to detect when the judge model updates and silently changes the criteria
- What is the minimum viable eval set for a low-risk product that doesn't make the business model unviable

---

## How this changes how I think about product

**Before:** eval was QA and engineering's responsibility. PM defines what to build, not how to test.

**After:** PM defines the quality criterion, the acceptance threshold, the eval method, and the consequence when the criterion isn't met. Engineering implements. If PM doesn't define it, engineering chooses — and that choice may not reflect the product's actual risk.

**Practical change:** any AI feature proposal I make from now on will include: (1) measurable quality criterion, (2) proposed eval method, (3) acceptance threshold with business justification, (4) what happens when the threshold isn't met.

**Narrative change:** I can now connect technical AI decisions (model choice, temperature, eval method) to business decisions (cost of error, risk tolerance, expected value). That's what differentiates a PM with AI depth from a PM who merely consumes AI.

---

## Open question

How do I define the minimum representative test set for an AI product in a regulated domain — without covering everything (infeasible) and without covering too little (risk)? Chapter 4 should provide the framework. If it doesn't, this is the central question for the next session.