# Raphael Santos · AI Products & Workflow Automation

Group Product Manager with 6+ years in regulated B2B products (fintech and market infrastructure). I design, build and run AI workflows end to end, from LLM integration and automation to human approval steps and guardrails.

Start with the first project below. It runs in production.

## Projects

### [Trello + Claude + Instagram Automation](products/trello-claude-instagram-automation/)
Status: live in production (private deployment). This release is open source.

An end-to-end content pipeline. Post ideas go in as Trello cards, Claude writes the copy, an AWS Lambda renders an on-brand image and stores it on S3, a person approves on Trello, and the Instagram Graph API publishes. Two n8n workflows connect the pieces. Any failure moves the card to an Error column with the reason attached.

What it shows: human-in-the-loop approval as a hard gate, guardrails against fabricated stats and duplicate publishing, and orchestration across Trello, Anthropic, AWS and Instagram APIs.

### [IBOV Analysis & Recommendation Agent](experiments/ibov_analysis_recommendation_agent/)
Status: working agent on live brapi.dev data (4 sandbox tickers without a token; full IBOV needs a paid plan).

A stock-analysis agent for Brazilian equities that combines technical and fundamental signals. I built two architectures side by side, a fixed pipeline with a single LLM call and a dynamic agent with a hand-written function-calling loop, to compare behavior and cost.

Core design rule: the model never sees raw market data and never computes a number. Fetch tools cache the raw data server side, compute tools run deterministic math, and the model only chooses tools and interprets computed results. Numeric hallucination is ruled out by construction, not by prompting.

Also: iteration cap, duplicate-call detection, tool errors returned for self-correction, every run logged to runs.jsonl as an evaluation dataset, and 32 offline tests.

### [job_extractor](experiments/job_extractor/)
A FastAPI service that turns a raw job posting into structured JSON through Anthropic tool use, called over plain HTTP without the SDK to make the request and response structure explicit.

### [job_assistant](experiments/job_assistant/)
A tool-use assistant with a tool registry and executor, running on Claude Haiku over a local job list (sample data included).

### [ai_chat_v1](products/ai_chat_v1/)
A chat app with a FastAPI backend that talks to the Anthropic API directly over HTTP (no SDK), streams tokens to the browser via Server-Sent Events and manages conversation state on its own, since the API is stateless.

### Career Multi-Agent (Flowise)
Status: Phase 1 running on Flowise. The flow is not in this repository. Phase 2 (LangGraph migration) is paused.

## Product discovery
[products/discovery/](products/discovery/) holds problem discovery, research results and decision logs for product bets, including the decisions to hold off on building.

## Stack
Python · FastAPI · Anthropic API (direct HTTP and Python SDK, tool use, streaming) · n8n · AWS Lambda · S3 · CloudFront · pytest · brapi.dev · Trello API · Instagram Graph API · Flowise

## Also in this repo
- [notes/](notes/) · study notes on AI engineering (LLMs, RAG, function calling, evals, agents)
- [experiments/](experiments/) · smaller hands-on experiments with APIs, prompting and automation

## Connect
- LinkedIn: [linkedin.com/in/raphael-santos-gpm](https://linkedin.com/in/raphael-santos-gpm)
- Website: [raphaelproductmanager.com](https://raphaelproductmanager.com)
