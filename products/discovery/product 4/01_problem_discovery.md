# Product 4 — Problem Discovery (working title)

> **Status:** Discovery not started — problem sketch only, paused deliberately before solutioning
> **Last updated:** July 19, 2026
> **Origin:** Personal-life application sketched on top of `experiments/ibov_analysis_recommendation_agent` (Chapter 6 — Agents exercise, AI Engineering by Chip Huyen)

---

## Origin

While closing out the IBOV Analysis & Recommendation Agent (a Chapter 6 exercise — technical + fundamentalist stock analysis agent, IBOV, brapi.dev), Raphael sketched a personal-life application built on top of it: a GUI with (a) a long-term portfolio registry with reports, and (b) a trading area where the agent pushes trade-signal notifications, Raphael confirms executed/not-executed, and a performance diary computes gain/loss only on confirmed executions (unconfirmed signals are stored but not counted, to avoid repeat-signaling on the same idea).

Raphael explicitly paused before deciding anything on this sketch:

> "não vou decidir nada, preciso rodar uma sessão de produto discovery para isolar o problema"

This file exists to hold that thread as a proper backlog item instead of letting it live only inside a single conversation.

---

## Working hypothesis: this may be two distinct jobs-to-be-done, bundled

The initial three-area sketch was reframed (not yet confirmed by Raphael) as possibly two separate jobs with different shapes:

| | Job A — Portfolio tracking | Job B — Trading signal + diary |
|---|---|---|
| Direction | Pull — Raphael checks it | Push — agent notifies Raphael (or pull, TBD — see open questions) |
| Frequency | Low | Agent-driven cadence |
| Error cost | Low | Higher — a bad or duplicated signal has real cost |
| Human loop | Read reports | Confirm executed / not-executed before the diary counts it |

If these are genuinely two jobs with different triggers, frequencies, and error tolerances, treating them as one product from day one is a risk worth surfacing before any build decision — not something to resolve by building both and seeing what sticks.

---

## Open Questions (isolating the problem — none answered yet)

| Question | Status | Notes |
|---|---|---|
| What does Raphael do manually today for each job (portfolio tracking vs. trading decisions)? | Unanswered | The real job/pain is in current manual behavior, not in what would be nice to have |
| Is the diary's real purpose personal accountability, or feedback to improve the agent's future signals? | Unanswered | Changes what "done" looks like for Job B — accountability log vs. training signal |
| Who decides trading cadence — agent-scheduled push, or Raphael pulling on demand? | Unanswered | Determines whether this is push-based at all |
| Confirm: is this app a separate initiative from the Chapter 6 exercise scope? | Pending confirmation | To be decided only after discovery concludes, not before |

---

## Next Steps

- [ ] Answer the 4 isolating questions above (Raphael leads; facilitation only, no recommendation until the problem is isolated)
- [ ] Determine whether Job A and Job B are one product or two
- [ ] Only after that: revisit what "a GUI" even means for this — the shape may not be a GUI at all
