# AI Product Journey — Raphael Santos

Public portfolio documenting my transition into AI product leadership.

I'm a Group Product Manager with 6+ years building regulated B2B products 
in fintech and market infrastructure. This repository captures my hands-on 
journey learning to build and ship AI-powered products — week by week, 
in public.

---

## What you'll find here

- **notes/** — Weekly learning notes on AI Engineering, LLMs, RAG, 
  function calling, evals and agents
- **products/** — AI products I'm building, with architecture, brief 
  and documented decisions
- **experiments/** — Hands-on experiments with APIs, prompting and automation

---

## Products

### ai_chat_v1
An Chat interface designed to communicate with Anthropic API,
made to understanding how communication with APIs works without
any SDK.
- Status : Done.

### Career Multi-Agent (Flowise)
An AI agent system designed to support career strategy, 
positioning and professional development.
- Status: Phase 1 live — Phase 2 in progress

### [Trello + Claude + Instagram Automation](products/trello-claude-instagram-automation/)
An end-to-end content pipeline: plan post ideas as Trello cards, Claude 
writes the copy, a Lambda renders an on-brand image, a human approves on 
Trello, and the Instagram Graph API auto-publishes. Two n8n workflows 
connect the pieces, with content-safety guardrails (no fabricated stats, 
no duplicate publishing) built in. Extracted and sanitized from a real 
production deployment into a reusable, brand-agnostic open-source release.
- Status: Live in production (private deployment) · this release is open source

---

## Stack

Python · OpenAI API · Anthropic API · Flowise · n8n · 
Streamlit · Supabase · pgvector · Railway

---

## Connect

- LinkedIn: [linkedin.com/in/raphael-santos-gpm](https://linkedin.com/in/raphael-santos-gpm)
- Website: [raphaelproductmanager.com](https://raphaelproductmanager.com)