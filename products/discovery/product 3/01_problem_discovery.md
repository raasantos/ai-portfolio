# Product 3 — Problem Discovery

> **Status:** Hypotheses defined · External research in progress · Results pending
> **Last updated:** May 13, 2026
> **Discovery phase:** Problem validation (pre-solution)

---

## Problem Statement

A significant portion of Brazilian middle-class adults have money saved but do not invest it. The initial assumption was that this was caused by a lack of financial knowledge or accessible investment tools. After initial analysis, this hypothesis was rejected.

Tools exist. Knowledge is increasingly available. The barrier appears to be emotional and behavioral — not informational.

---

## Hypothesis Evolution

### H1 — Initial hypothesis (rejected)

> "People don't invest more because they lack financial knowledge and accessible investment tools."

**Why it was rejected:**
- The Brazilian market already has accessible investment platforms (NuInvest, Warren, Rico, BTG Digital) with low minimums and simple onboarding
- Financial education content is abundant (YouTube, Instagram, podcasts)
- The target segment already uses Nubank — NuInvest is two taps away
- Saying "tools are missing" in 2026 is a claim that cannot be defended

### H2 — Refined hypothesis (under validation)

> "People with monthly income up to R$5,000 and savings up to R$20,000 are blocked by emotional and behavioral barriers — not by lack of information or tools — from making their first investment."

**Origin:** Direct observation of a social circle matching the target segment. Multiple people with savings behavior who have not taken the step toward investing despite having access to the same tools as active investors.

**Key insight:** These people already demonstrate saving discipline. The gap is not between spending and saving — it is between saving (poupança, conta corrente) and investing. The behavior is partially formed. The final step is blocked.

---

## Segment Definition

| Attribute | Definition | Rationale |
|---|---|---|
| Monthly income | Up to R$5,000 | Middle-class profile with some disposable income but cost-of-living pressure |
| Saved amount | Up to R$20,000 | Enough to invest, not enough to afford a human financial advisor |
| Age range | 18–50 | Broad enough to observe across life stages; narrows in validation |
| Country | Brazil | Observation context; regulatory environment is Brazil-specific |
| Saving behavior | Active — money is being set aside | Critical signal: the problem is not financial discipline, it is the next step |
| Investment status | None or poupança only | Baseline behavior to validate |

**What this segment is not:**
- High-income investors who already operate in the market
- People with no savings capacity
- Professional investors or anyone with financial market background

---

## Problem Hypotheses

These are hypotheses derived from direct observation. Not yet validated by external research.

### PH1 — Fear of loss (primary)
People believe investing means a high probability of losing money. This belief persists even for low-risk instruments (CDB, Tesouro Direto, LCI/LCA). The emotional framing is "I could lose everything" rather than "I could lose 2% in a bad year."

**Signal:** Verbal expression — "Tenho medo de perder meu dinheiro."

### PH2 — Perceived complexity
The mental model of investing is one of high technical demand: charts, tickers, market timing, complex decisions. The gap between "what I know" and "what I think I need to know" feels too large to bridge.

**Signal:** Verbal expression — "É muito complicado, não entendo nada disso."

### PH3 — Decision paralysis
The person knows they should invest. They have the money. They cannot take the first step. This is not lack of motivation — it is paralysis in front of a decision that feels irreversible and consequential.

**Signal:** "Tenho dinheiro parado mas não sei o que fazer com ele."

### PH4 — Distrust in financial institutions
Banks are perceived as adversarial. The assumption is that any product recommended by a bank benefits the bank first. This distrust extends to newer platforms, which are perceived as "the same but digital."

**Signal:** "Fui no banco e saí mais confuso do que entrei."

---

## What Existing Solutions Don't Seem to Solve

This section documents the gap between available tools and the observed behavior. These are hypotheses — not validated answers.

Apps like Warren, NuInvest, and Rico exist and are accessible. Yet the segment is not using them. Possible explanations — to be validated:

- Onboarding starts with product choice, not with emotional readiness
- The interface assumes the user already wants to invest; it does not address the fear of the first step
- There is no trusted, patient entity answering "but what happens if I lose it all?" at 11pm
- The apps optimize for conversion, not for confidence building

**The open question this generates:** Is the gap a product design problem, a trust problem, or a distribution problem?

---

## Open Questions

These must be answered before any solution discussion.

| Question | Why it matters |
|---|---|
| Why don't Warren and NuInvest already solve this for this segment? | If they do, the opportunity may not exist |
| Is there willingness to pay for a solution in this income range? | Determines whether B2C is viable or if B2B2C is required |
| What is the regulatory path for an investment-adjacent product in Brazil? | CVM rules on investment advice could constrain the solution space significantly |
| What specific moment does this pain peak? | Needed to understand the trigger and the context of use |
| Does this segment appear in public data outside the observed social circle? | Validates whether this is a real market signal or a local observation |
| Is the barrier consistent across the 18–50 age range, or segment-specific? | May require narrowing the target segment after validation |

---

## Research Methodology

To validate or refute H2 and the problem hypotheses above, external research was designed using two tools and two sources.

### Source 1 — X (via Grok)
Target: spontaneous Portuguese-language expressions of investment frustration on social media.

Focus expressions:
- "não sei por onde começar a investir"
- "tenho medo de perder meu dinheiro"
- "quero investir mas não sei como"
- "deixei na poupança porque"
- "dinheiro parado"
- "fui no banco e não entendi nada"

Expected output: raw sentiment table, barrier frequency, workaround behavior, emotional language patterns.

### Source 2 — Reddit and web (via ChatGPT Deep Research)
Target: r/investimentos, r/financaspessoais, r/brasil, r/desabafos, YouTube comments on beginner investment content, Infomoney and Exame Invest comment sections.

Expected output: segment profile from public data, barrier frequency analysis, workaround mapping, opportunity signal table, gaps and risks.

Full research prompts are in the appendix.

---

## Research Results

> **Pending.** External research was initiated on May 13, 2026. Results will be added to `02_research_results.md` once available.

---

## Next Steps

- [ ] Run Grok research prompt and collect raw output
- [ ] Run ChatGPT Deep Research prompt and collect raw output
- [ ] Document results in `02_research_results.md`
- [ ] Analyze results against H2 and problem hypotheses
- [ ] Decide: validate, refine, or discard H2
- [ ] If validated: move to segment interviews or secondary research on solution space

---

## Appendix — Research Prompts

### Prompt A — Grok (X/Twitter)

```
You are a product discovery researcher. Your task is to find real evidence
of people expressing frustration, fear, or emotional blocking around
starting to invest money.

Focus: Brazil, Portuguese language, individual middle-class adults
(not professional investors, not business owners).

Search X (Twitter) for posts containing expressions such as:
- "não sei por onde começar a investir"
- "tenho medo de perder meu dinheiro"
- "quero investir mas não sei como"
- "deixei na poupança porque"
- "investi e me arrependi"
- "não confio em investimento"
- "é muito complicado investir"
- "queria investir mas"
- "tenho dinheiro parado"
- "fui num banco e não entendi nada"

For each pattern found, produce:

Table 1 — Evidence collected
| Source | Real quote or close paraphrase | Dominant emotion |
Apparent segment (age/context) | Current workaround mentioned |

Table 2 — Frequency and intensity
| Barrier type | Mention frequency (high/medium/low) |
Emotional intensity (1–5) | Most common spontaneous language |

Sentiment analysis
Classify dominant emotions found in order of frequency. Identify whether
the sentiment is fear of loss, shame for not knowing, frustration with
complexity, distrust in institutions, or other.

Workaround patterns
What do these people do instead of investing?
Poupança, leaving money in checking account, keeping cash at home, other?

Pain intensity signal
Is there a specific moment or trigger when this frustration appears
more frequently? (ex: receiving 13th salary, economic news, friends
talking about investments)

Do not suggest solutions. Only map the problem as it appears in
people's spontaneous language.
```

---

### Prompt B — ChatGPT Deep Research (Reddit, forums, web)

```
You are a product discovery researcher conducting a problem validation
study. Your task is to find public evidence that people with monthly
income up to R$5,000 and some money saved (up to R$20,000) face emotional
and behavioral barriers to starting to invest in Brazil.

Search the following sources:
- Reddit: r/investimentos, r/financaspessoais, r/brasil, r/desabafos
- Brazilian personal finance forums
- YouTube comments on beginner investment videos
- Comment sections on Infomoney, Exame Invest, Suno articles

Look for real accounts indicating:
1. Fear of losing money as a reason not to invest
2. Perceived complexity as a barrier ("I don't understand any of this")
3. Lack of confidence to make the decision
4. Bad prior experiences that created paralysis
5. Money sitting idle due to indecision, not lack of interest

Deliverable 1 — Evidence table
| Source | Summarized account | Main barrier identified |
Dominant emotion | Current solution used by the person |

Deliverable 2 — Sentiment analysis by barrier type
| Barrier | Estimated % of mentions | Most common language |
Intensity (1–5) |

Deliverable 3 — Segment analysis
Based on accounts found, what profile appears most frequently?
(apparent age range, life context, declared financial knowledge level)

Deliverable 4 — Opportunity signal
| Indicator | Observation |
| Pain frequency | |
| Emotional intensity | |
| Current workaround | |
| Dissatisfaction with workaround | |
| Willingness to pay signal | |
| Competition as perceived by users | |

Deliverable 5 — Gaps and risks
What could the research not confirm? Which hypotheses remain without
evidence?

Critical rule: do not invent data. If evidence is insufficient for any
field, mark as "insufficient" and indicate where to search further.
Do not suggest solutions anywhere in the response.
```
