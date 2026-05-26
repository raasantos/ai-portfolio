# Product 3 — Problem Discovery

> **Status:** Problem validated · Solution discovery complete · MVP scope pending
> **Last updated:** May 20, 2026
> **Discovery phase:** Solution validated — moving to experiment design

---

## Problem Statement

A significant portion of Brazilian middle-class adults have money saved but do not invest it. The initial assumption was that this was caused by a lack of financial knowledge or accessible investment tools. After initial analysis, this hypothesis was rejected.

Tools exist. Knowledge is increasingly available. The real barrier is not informational — it is a three-layer combination of emotional, cognitive, and trust-based obstacles that prevent people from taking the final step from saving to investing.

The user journey mapping (May 20, 2026) revealed the core insight: **it is the same person on both paths.** Whether someone invests or not depends on whether they have access to a trusted guide at the moment of decision — not on knowledge, willpower, or tools.

---

## Hypothesis Evolution

### H1 — Initial hypothesis (rejected)

> "People don't invest more because they lack financial knowledge and accessible investment tools."

**Why it was rejected:**
- The Brazilian market already has accessible investment platforms (NuInvest, Warren, Rico, BTG Digital) with low minimums and simple onboarding
- Financial education content is abundant (YouTube, Instagram, podcasts)
- The target segment already uses Nubank — NuInvest is two taps away
- Saying "tools are missing" in 2026 is a claim that cannot be defended

### H2 — Refined hypothesis (partially validated)

> "People with monthly income up to R$5,000 and savings up to R$20,000 are blocked by a three-layer barrier — emotional, cognitive, and trust-based — from making their first investment."

**Origin:** Direct observation of a social circle matching the target segment. Multiple people with savings behavior who have not taken the step toward investing despite having access to the same tools as active investors.

**Key insight:** These people already demonstrate saving discipline. The gap is not between spending and saving — it is between saving (poupança, conta corrente) and investing. The behavior is partially formed. The final step is blocked.

**Revised framing (May 13, 2026):** The barrier is not purely emotional. It is three distinct layers:
1. **Emotional** — fear of loss, anxiety, shame, low confidence
2. **Cognitive** — perceived complexity, lack of operational knowledge
3. **Trust** — distrust in banks, advisors, platforms, financial "gurus"

**Why the three-layer framing matters:** Calling it purely emotional would lead to a solution focused only on reassurance. The cognitive and trust layers require different interventions. Conflating them produces a product that partially solves the problem.

### H3 — Structural gap hypothesis (derived May 20, 2026)

> "The segment has access to a guide (bank manager) but cannot trust them due to conflict of interest. The trustworthy guide (independent advisor) is inaccessible at this income level. The accessible guide is not trustworthy. The trustworthy guide is not accessible."

**Origin:** User journey mapping exercise — two-path diagram based on empirical observation of real people in the target segment who asked for investment guidance.

**What the journey revealed:**
- The trigger question is always specific: *"Você sabe onde posso colocar meu dinheiro em um lugar que rende mais que a poupança?"*
- The person who invests found someone to ask this question and received a trustworthy, personalized answer
- The person who does not invest tried to navigate alone, hit fear and complexity, and defaulted to the workaround
- The difference is not knowledge or courage — it is access to a trusted guide at the right moment

---

## Segment Definition

| Attribute | Definition | Rationale |
|---|---|---|
| Monthly income | Up to R$5,000 | Middle-class profile with some disposable income but cost-of-living pressure |
| Saved amount | Up to R$20,000 | Enough to invest, not enough to afford a human financial advisor |
| Age range | 18–50 (skews 19–25 in external data) | Broad hypothesis; external research showed younger concentration |
| Gender | Predominantly male | 70%+ of active Brazilian investors are male (national population data) |
| Country | Brazil | Observation context; regulatory environment is Brazil-specific |
| Saving behavior | Active — money is being set aside | Critical signal: the problem is not financial discipline, it is the next step |
| Investment status | None or poupança / daily liquidity accounts only | Baseline behavior to validate |

**What this segment is not:**
- High-income investors who already operate in the market
- People with no savings capacity
- Professional investors or anyone with financial market background

**Segment note:** The 25–50 age group behavior has not been separately validated. External research skewed 19–25. Whether barriers are consistent across the full range requires further investigation.

---

## Problem Hypotheses

### PH1 — Fear of loss (validated)
People believe investing means a high probability of losing money. This belief persists even for low-risk instruments (CDB, Tesouro Direto, LCI/LCA). The emotional framing is "I could lose everything" rather than "I could lose 2% in a bad year."

**Signal:** "Tenho medo de perder meu dinheiro." / "Suando frio só de pensar."
**Validation:** Confirmed in both Grok and Reddit research. Intensity 5/5.

### PH2 — Perceived complexity (validated)
The mental model of investing is one of high technical demand: charts, tickers, market timing, complex decisions. The gap between "what I know" and "what I think I need to know" feels too large to bridge.

**Signal:** "É muito complicado, não entendo nada disso." / "Conhecimento 0."
**Validation:** Most frequent barrier — 35% of Reddit mentions.

### PH3 — Decision paralysis (validated)
The person knows they should invest. They have the money. They cannot take the first step. This is not lack of motivation — it is paralysis in front of a decision that feels irreversible and consequential.

**Signal:** "Tenho dinheiro parado mas não sei o que fazer com ele."
**Validation:** Consistent workaround pattern across both sources.

### PH4 — Distrust in financial institutions (validated)
Banks are perceived as adversarial. The assumption is that any product recommended by a bank benefits the bank first. This distrust extends to newer platforms, which are perceived as "the same but digital."

**Signal:** "Fui no banco e saí mais confuso do que entrei." / "Não confio em homens falando sobre."
**Validation:** Confirmed in Grok, stronger than expected.

---

## User Journey Map

*Derived from empirical observation — May 20, 2026*

```
                    Euforia /              Falta de
                    Ganância           Conhecimento + Medo
                       ↓                      ↓
[Quero Investir] → [Onde Rende   →  [Mas será que    →  [Será que tem    →  [Vou deixar
 Meu Dinheiro]      Mais?]           posso perder        uma opção           na caixinha
                       |             meu dinheiro?]      melhor que          mesmo]
                       |          Aversão a perdas,      poupança?]
                       ↓          ignorância
               [Será que posso
                consultar alguém?] → [Você sabe onde   →  [Espera       →  [Aplica
                                      posso por meu        Confirmação      dinheiro]
               Busca Ajuda Externa    dinheiro que é        e validação]
                                      melhor que
                                      poupança?]
                                   Faz esse tipo
                                   de pergunta
```

**Key insight from the map:** The fork between the two paths happens at "Onde Rende Mais?" The person who invests found someone to ask a specific question and received a trustworthy answer. The person who doesn't invest tried to self-navigate and hit the barrier wall alone. Same person, different access to a trusted guide.

---

## What Existing Solutions Don't Solve

Apps like Warren, NuInvest, and Rico exist and are accessible. Yet the segment is not using them.

**Root cause identified (May 20, 2026):** The issue is not that platforms are missing. It is that the available platforms do not provide what the user journey requires: a trusted, patient entity that walks someone through a personalized decision at the moment they need it.

- Platforms optimize for conversion, not for confidence-building
- The interface assumes the user already wants to invest; it does not address the fear of the first step
- Bank managers are accessible but conflicted — they are remunerated by product acquisition
- Independent advisors are trustworthy but inaccessible at this income level
- YouTube and Reddit provide free generic education but not personalized decisions

**The gap:** Accessible but not trustworthy (bank) vs. trustworthy but not accessible (independent advisor).

---

## Open Questions

| Question | Status | Notes |
|---|---|---|
| Will this segment pay R$20/month for neutral guidance? | **Critical — unvalidated** | Primary learning objective of the MVP experiment |
| Does education framing (without explicit recommendation) drive action? | **Critical — unvalidated** | Central learning question of the MVP |
| Why don't Warren and NuInvest already solve this for this segment? | Hypothesis only | Root cause identified as trust + no personalized guidance, not technology |
| Is the barrier consistent across 25–50, or specific to 19–25? | Unvalidated | External research skewed younger; needs separate investigation |
| What specific investment options to present in MVP? | Decision needed before build | CDB, LCI/LCA, Tesouro Direto, FIIs — or subset? |
| Static options or real-time market data in MVP? | Decision needed before build | Real-time is likely out of 1-week scope |

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

External research completed May 13, 2026. Full results in `02_research_results.md`.

**Summary of findings:**
- All four problem hypotheses validated across both sources
- ANBIMA national data: 33% of Brazilians saved in 2025, only 10% invested in financial products
- Dominant workarounds: Nubank caixinha, poupança, dinheiro parado
- Willingness to pay: insufficient evidence — segment defaults to free solutions
- Segment age: external data skews 19–25, younger than hypothesized

---

## Next Steps

- [x] Run Grok research prompt and collect raw output ✅
- [x] Run ChatGPT Deep Research prompt and collect raw output ✅
- [x] Document results in `02_research_results.md` ✅
- [x] Analyze results against H2 and problem hypotheses ✅
- [x] Solution discovery session completed ✅ — see `04_solution_discovery.md`
- [ ] Define specific investment options for MVP
- [ ] Decide: static options or real-time data?
- [ ] Design $100 experiment with payment mechanic
- [ ] Scope 1-week build

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