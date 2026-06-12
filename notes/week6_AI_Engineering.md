# Week 6 — AI Engineering: Chapter 5

**Date:** June 11, 2026
**Chapter covered:** Chapter 5 (Prompt Engineering)
**Recall score:** 6/10 → gaps closed in session

---

## 8 observations I made (not a summary, what caught my attention)

1. **Prompt engineering is the cheapest model adaptation technique, but "cheap to start" doesn't mean "easy to do well."** Anyone can write a prompt. The real skill is writing one that holds up under varied inputs, edge cases, and adversarial use. The book makes a useful distinction: easy to get started, hard to get right. This maps directly to how I think about product features. Low barrier to entry creates the illusion of mastery before the real complexity shows up.

2. **In-context learning reframed how I think about examples in prompts.** I knew that adding examples improved outputs. I didn't know why. The mechanism is that the capability already exists in the model's weights. Examples don't teach the model anything new. They activate the right program and narrow the interpretation space. This explains why few-shot matters more for domain-specific tasks: if the model has weak priors on your domain, examples compensate. Generic tasks need fewer examples because the model already has strong priors.

3. **Lost in the middle is a design constraint, not a research curiosity.** The finding that models process the beginning and end of a prompt better than the middle is easy to dismiss as a benchmark result. It's not. It directly affects how I structure system prompts in my agents. If I have a critical instruction — say, a constraint the model must always follow — and I bury it in the middle of a 500-token system prompt, I'm accepting performance degradation by design. This one I'm fixing immediately.

4. **Prompt decomposition is something I was already doing without the name.** The job_extractor is a decomposed chain: structured output from one API call feeds the next step. What I didn't have was the vocabulary or the full picture of why it works. The four benefits — monitoring, debugging, parallelization, cost control — are things I've felt the absence of when working with monolithic prompts. Naming them makes it easier to defend the architectural decision in a conversation or interview.

5. **The connection between prompt decomposition and agents clicked during gap closure.** A fixed chain is decomposition. A dynamic chain — where the next step depends on the previous output — is an agent. That progression (single prompt → CoT → decomposition → agent) makes the complexity feel earned instead of arbitrary. Flowise and n8n are just visual interfaces for that same chain logic. Under the hood it's API calls.

6. **Silent template errors are the most dangerous failure mode in this chapter.** Not jailbreaking. Not prompt injection. Template errors. Because they produce no signal. The model responds. The output looks reasonable. You never know the template was wrong unless you inspect what the model actually received. I've used LangChain. I never checked the templates. This is a gap in how I've been building.

7. **Indirect prompt injection changes the threat model for any agent with tool access.** Once a model can read emails, browse documents, or search the web, the attacker's surface area explodes. They don't need to get into your system. They just need to put malicious instructions somewhere your agent will retrieve. This isn't theoretical — the email forwarding example in the book is exactly the kind of thing that would happen in a personal assistant agent. Any agent I build with external tool access needs output guardrails and human approval gates for irreversible actions.

8. **The instruction hierarchy is the cleanest solution I've seen to the prompt injection problem.** Train the model to treat system prompt > user prompt > model output > tool output as a priority order. When instructions conflict, higher priority wins. Tool outputs have the lowest priority, which is exactly right — they're the attack vector. This doesn't require changing the prompt. It requires training. Which means it's a model-level property, not something application developers can fully control. Worth knowing when evaluating which models to use in a production agent.

---

## Questions I had and how I closed them

**How is prompt decomposition actually implemented if it's not a single-prompt technique?**

It's separate API calls chained in code or a workflow tool. Prompt 1 runs, produces Output 1. Output 1 becomes input for Prompt 2. And so on. The simplest version is sequential Python calls to the API — no framework needed. Flowise and n8n abstract that logic visually. This doesn't work inside a chat session because a chat is a single session with a single model. You can simulate steps inside a conversation, but you lose monitoring, parallelization, and cost control per step.

**Why is it called prompt decomposition if it needs more than prompts to implement?**

The name refers to where the design decision happens, not where the implementation lives. You decompose the task at the prompt design level — deciding how to break the problem before writing any code. The name stuck because that's where the thinking happens. The implementation requires more layers, but the decision is a prompting decision.

**Are all prompt engineering tools transparent about their templates?**

Not all. Open-source tools like LangChain expose templates and allow overrides. Others are more opaque. The book's point is that you often don't know what's inside a tool until something breaks — and by then you've been debugging a silent failure. Writing prompts manually first means you know exactly what the model receives. That baseline makes tool errors detectable instead of invisible.

---

## How this changes how I think about product and building

**Before:** I structured system prompts based on intuition. Important instructions went where they felt logical, usually in the middle of a block of text describing the agent's role and constraints.

**After:** important instructions go at the beginning or end of the system prompt. Not in the middle. This is a direct consequence of lost in the middle and costs nothing to fix.

**Before:** I used LangChain templates without checking what was inside them.

**After:** any tool I use gets inspected at the template level before I trust its output. If I can't see the template, I write the prompt manually first and use the known-good output as a reference.

**Before:** I thought about agents as a distinct category from prompt decomposition.

**After:** agents are decomposition with dynamic routing added. The architecture is the same. The difference is whether the chain is fixed or decision-driven. This makes it easier to reason about where to start when building a new agent: start with a fixed decomposed chain, validate each step, then add routing logic if the task requires it.

**Open question for next chapters:** RAG is mentioned in this chapter as a context construction tool. Chapter 6 covers it. The question I'm carrying forward: when is RAG the right solution versus providing context directly in the prompt? The chapter hints at it but doesn't answer it.

---

## Key concepts for interview readiness

1. **In-context learning:** models learn from examples in the prompt without updating weights. Before GPT-3, new tasks required retraining. Few-shot narrows interpretation. Zero-shot has no examples. More shots cost more tokens.
2. **Lost in the middle:** models process beginning and end of prompts better than the middle. Critical instructions should not be buried. Validated by needle in a haystack (NIAH) test.
3. **CoT (Chain-of-Thought):** "think step by step" forces intermediate reasoning before the final answer. Reduces errors and hallucinations on reasoning tasks. Increases latency. Single-prompt technique.
4. **Prompt decomposition:** breaking complex tasks into subtasks with separate API calls. Enables monitoring, debugging, parallelization, and cost control. Foundation of agent architecture. Not a chat-based technique.
5. **Silent template errors:** wrong chat template produces worse output with no error signal. Inspect tool templates before trusting output. Start with manual prompts.
6. **Instruction hierarchy:** system prompt > user prompt > model output > tool output. Model-level defense against prompt injection. Tool outputs have lowest priority by design.
7. **Indirect prompt injection:** malicious instructions placed in external content the model retrieves via tools. More dangerous than direct injection because the attack surface is external. Defense: output guardrails, human approval for irreversible actions.