# Week 5 — AI Engineering: Chapter 4

**Date:** May 26–28, 2026
**Chapter covered:** Chapter 4 (Evaluate AI Systems)
**Recall score:** 8.5/10

---

## 10 observations I made (not a summary, what caught my attention)

1. **If your company's strategy is not being an AI company, over-investing in self-hosting AI can cost you sight of your own strategy.** The build vs buy decision isn't just technical. When a company uses AI as leverage for differentiation, not as their core product, the cost of maintaining models, infrastructure, and a specialized team can divert attention from the actual business. Start with commercial APIs. Migrate to self-hosted only when it's validated and justified.

2. **Hard attributes work as sequential go/no-go gates before you spend a dollar on benchmarks.** The book lists 7 axes for build vs buy (data privacy, data lineage, performance, functionality, costs, control, on-device deployment). But in practice, you don't evaluate all 7 in parallel. Privacy is a go/no-go gate. Copyright and data lineage are a go/no-go gate. If a model fails either, it's out before you benchmark anything. This reduces the decision space fast and saves time and money.

3. **Time-to-market inclines toward commercial models, and that's a product decision.** Companies rarely have unlimited time to evaluate. In my experience, speed often means partnering with a commercial provider first, then building a migration path to self-hosted if the economics or control requirements justify it later. A junior PM picks A or B. A senior PM picks A now with a path to B if validated.

4. **Eval is not a final test. It's a continuous diagnostic system.** Eval isn't just about accuracy. It serves to find gaps in the application. It helps define what data you need for refinement. It detects when model changes silently degrade your product. And it tells you where improvement effort should go next. Treating eval as a one-time gate before launch misses most of its value.

5. **Evaluation-driven development is the right starting point, but product strategy should drive the criteria.** The book says define eval criteria before building, inspired by test-driven development. I agree with the principle, but there's a risk: defining eval criteria in isolation can bias you toward the solution rather than the problem. If the product strategy already defines success metrics (DAU, conversion, retention), those business metrics should drive which eval criteria matter. Not the other way around.

6. **Eval metrics must be tied to business outcomes, or they're just numbers.** The book gives a concrete example: factual consistency at 80% means automating 30% of customer support. At 90%, 50%. At 98%, 90%. This is the connection that makes eval a product decision. The chain is: business metric, then which eval metric drives it, then measure that. Without this mapping, a score of 80% means nothing to a stakeholder.

7. **For my investment product, global factual consistency is the floor, but domain-specific eval is the real requirement.** I don't control the model's training data, so the general knowledge about markets and investments is what drives answer quality. But global factual consistency alone isn't enough. If the model gives wrong information about a specific financial product, the damage is high. So I need domain-specific eval for regulatory risk on top of general factual consistency.

8. **Data slicing should be iterative, not exhaustive upfront.** The book says to slice evaluation data into subsets (by user type, format, topic, traffic source) for finer-grained understanding. My take: you don't need to define every slice in the first evaluation. Start with 2-3 meaningful subsets, analyze results, and let the data generate hypotheses for further slicing. "Why does one model perform better overall but worse in each subgroup?" That question leads to the next subset to investigate.

9. **The aggregate score can lie. Simpson's paradox makes slicing non-optional.** Model A can outperform Model B on aggregate data but underperform on every individual subgroup. This happens when subgroups have very different sizes. If you only look at the overall score, you pick the wrong model. Slicing isn't a nice-to-have. It's a safeguard against misleading results.

10. **Test set sizing has a practical rule I can use in product decisions.** My open question from Chapter 3 was: how do I define the minimum representative test set? Chapter 4 answered it. The rule: for every 3x decrease in the score difference you want to detect, you need 10x more samples. Detecting a 30% difference needs ~10 samples. 10% needs ~100. 3% needs ~1,000. 1% needs ~10,000. To validate if the size is sufficient: bootstrap. Resample with replacement, run eval multiple times. If results vary wildly, the set is too small.

---

## Questions I had and how I closed them

**How do I version eval prompts and detect when a judge model silently changes scoring?**

Pin the model version. Use `claude-sonnet-4-20250514`, not just "claude-sonnet". If the provider updates the model without you knowing, your eval results shift and you don't know why.

Then keep a golden set, something like 10-20 examples with known expected scores. Run it periodically. If scores drift beyond a threshold, the judge changed, not the application. Investigate before trusting new results.

And version everything. Each eval prompt gets a version number. Each eval run logs: prompt version, judge model version, date, results. So when something shifts, I can trace if it was the application or the judge. Treat the eval prompt as product code. Versioned, tested, never changed silently.

**How do I balance eval cost against product margin when revenue is uncertain?**

The real question is not "can I afford eval?" but "can I afford an undetected failure?" In my investment product, one wrong recommendation that a user acts on is more expensive than running eval on 100 samples weekly.

So the approach is tiered. Cheap automated metrics (regex, exact match, classifier) on 100% of outputs. Expensive AI judge on 1-5% sample. Human review on a smaller subset when stakes are high. This gives signal at every price point.

And the sizing rule helps here too. Early stage, I only need to detect large differences, 30% or more, so ~10 samples is enough. As the product matures and differences get smaller, I invest proportionally. Early-stage eval should be cheap and rough, not cheap and absent.

**When is meta-evaluation worth it versus overhead?**

If I would make a launch, pricing, or model-swap decision based on the eval score, I meta-evaluate first. If I'm using eval just for directional signal during exploration, I don't.

So it's worth it when the score difference between two models is small and I need to trust the eval to pick the right one. Or when scores look good but users complain. Or in regulated domains where eval results become part of compliance documentation.

It's overhead when I'm just trying things, when the criteria is binary pass/fail (did it return valid JSON? yes/no), or when the product is low-risk and a wrong eval doesn't lead to a wrong decision with consequences.

---

## How this changes how I think about product

**Before:** model selection was a technical decision. Engineering picks the model, PM defines the features.

**After:** model selection is a product decision with a structured workflow. PM defines the hard attribute filters (privacy, copyright, compliance). Uses benchmarks to narrow candidates. Then runs custom eval against product-specific criteria. The PM also owns the connection between eval scores and business outcomes. Without that mapping, eval is just a technical exercise.

**Practical change:** any AI model selection I participate in will follow this sequence: (1) filter by hard attributes as go/no-go gates, (2) narrow with relevant public benchmarks, (3) run custom eval pipeline with product-specific criteria tied to business metrics, (4) monitor in production and iterate. I won't treat benchmark leaderboards as the answer. They filter bad models but can't find the best one for my application because of data contamination and benchmark correlation.

**Open question resolved:** the test set sizing rule (3x diff to 10x samples) and bootstrap validation method answer my Chapter 3 question about minimum representative test sets. This is now a tool I can use in product proposals to justify eval investment.

---

## Key concepts for interview readiness

1. **Evaluation-driven development:** define eval criteria before building. "How will we know if this works?" is the first question, not the last.
2. **Hard vs soft attributes:** hard = can't change (license, privacy, training data). Soft = can improve (accuracy, style, toxicity). Filter by hard first.
3. **Test set sizing:** 3x smaller difference to detect means 10x more samples needed. Bootstrap to validate sufficiency.
4. **Data contamination:** benchmarks trained on can't be trusted. Two detection methods: n-gram overlapping (precise, expensive, needs training data access) and perplexity (cheaper, less precise).
5. **Simpson's paradox:** always slice. Aggregate scores can mislead when subgroups have different sizes.
6. **Tie eval to business metrics:** a factual consistency score means nothing without mapping to a business outcome. 80% consistency means 30% of requests automated. That's the number that matters.