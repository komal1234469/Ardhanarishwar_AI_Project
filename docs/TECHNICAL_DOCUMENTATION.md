# Ardhanarishwar — Technical Documentation

## Product Vision

A global, AI-first, human-backed platform solving two connected problems:

**1. Candidate problem.** Many people — from skilled graduates to unskilled first-time job
seekers — have a gap between what they know and what employers/the market need. Skilled
users need gap analysis and better-matched opportunities; unskilled users need step-by-step,
practical, foundational training to become job-ready.

**2. Business/client problem.** Business owners face real-world problems (declining sales,
finding B2B clients, hiring the right people) and often don't have in-house expertise or time
to solve them immediately.

**The core USP** is not "we built an AI chatbot" — it is "we built an AI-first platform that
tries to solve the problem immediately using GenAI + RAG, and automatically escalates to a
verified human expert within 24 hours whenever the AI isn't confident enough." This AI +
Human hybrid model is what makes the platform trustworthy at both individual and business
scale.

## Prototype Architecture

```
                        OUR PLATFORM
                             │
                 ┌───────────┴───────────┐
                 │                       │
          CANDIDATE SIDE            BUSINESS SIDE
        (Skilled / Unskilled)      (Business problem)
                 │                       │
                 └───────────┬───────────┘
                             ↓
                    Security & Sanitization
                    (input cleaning, prompt-
                     injection detection)
                             ↓
                    Local RAG Retrieval
                 (TF-IDF over knowledge base)
                             ↓
                 ┌───────────┴───────────┐
                 │                       │
        Confidence ≥ threshold    Confidence < threshold
        OR local LLM available     AND no local LLM
                 │                       │
                 ↓                       ↓
        AI-generated answer      Escalate to Human
        (Ollama local LLM or      Expert Desk (queued
         rule-based fallback)     with question, mode,
                 │                 candidate type, AI
                 │                 confidence score)
                 └───────────┬───────────┘
                             ↓
                   SQLite: messages, feedback,
                   escalations (for admin + audit)
                             ↓
                    Response shown to user
```

Browser UI (Streamlit) → Session/Memory → Mode & Candidate-Type Router → Local RAG →
Local LLM (optional) or rule-based fallback → Confidence check → AI answer **or** Human
Escalation → Response → SQLite (messages / feedback / escalations).

## No Third-Party AI API

The prototype does not require OpenAI/Gemini/Anthropic API keys. Optional GenAI inference
uses an Ollama-compatible local open-source model (`llama3.2:3b`). If Ollama isn't running,
the platform still answers using retrieval + rule-based logic, and escalates genuinely
low-confidence queries to a human instead of fabricating an answer.

## RAG

Prototype: local knowledge file (`data/knowledge_base.txt`, now including a dedicated
**Skilled track**, **Unskilled/first-time job seeker track**, **business escalation model**,
and **global vision** section) → chunked by blank line → TF-IDF vectors → cosine similarity.

Production: PDF/DOCX/HTML ingestion → metadata-aware chunking → multilingual embeddings
(to support a global, multi-language user base) → FAISS/Qdrant → reranker → grounded
generation with citations.

## AI-First, Human-Backed Escalation Model

This is the platform's key trust mechanism, implemented in `src/assistant.py`:

- Every query first gets a local RAG retrieval-confidence score.
- If that score is below a threshold **and** no local LLM (Ollama) is available to reason
  further, the query is **not** answered by guessing — it is logged to an `escalations`
  table (`src/database.py`) with the session, mode, candidate type (Skilled/Unskilled) and
  the AI's confidence score, and the user is told a human expert will respond within 24
  hours.
- The **Admin & Escalations** tab in the UI acts as the Human Escalation Desk: staff can
  filter pending/resolved escalations, read the original question, and record a resolution.
- Production version: this becomes a real ticketing/SLA system (e.g. integrated with a
  helpdesk tool), with automatic reminders and analytics on escalation volume by topic —
  directly showing where the knowledge base needs to grow.

This mirrors the requested design: **AI tries first → if unresolved, a human expert
verifies and responds within a committed time window**, rather than an AI that pretends to
always know the answer.

## Candidate Segmentation — Skilled vs. Unskilled (Global Vision)

- **Skilled track:** candidate already has some skills/education; the platform does gap
  analysis against a target role, recommends specific missing skills, practical projects,
  and suitable companies, and prepares them for interviews.
- **Unskilled / first-time job seeker track:** candidate may have little formal education or
  experience; the platform breaks a target role into small foundational steps, favors
  practical/vocational learning over theory, builds confidence with small real tasks, and
  matches them to entry-level or apprenticeship opportunities.
- This segmentation is designed to scale globally — the same architecture serves a computer
  science graduate in Kanpur and a first-time job seeker anywhere with equal seriousness,
  just with a different learning path.

## Agentic AI (Production Roadmap)

1. Intent Agent
2. Knowledge Agent
3. Career Agent (skilled track)
4. Foundational Training Agent (unskilled track)
5. Resume Agent
6. Interview Agent
7. Learning Agent
8. Recruitment Agent
9. Business Agent
10. Human-Escalation/Safety Agent — decides confidently-answerable vs. escalate

Agents use permission-controlled tools and audit logs. No unrestricted code execution.

## Voice

Production: Voice Audio → VAD → local Whisper/faster-whisper STT → agent/RAG/LLM → local
Piper TTS → audio stream.

## Memory

Short-term recent turns; long-term explicit goals/preferences with consent; enterprise
memory scoped by tenant.

## Security

TLS, encryption at rest, OAuth/SSO, RBAC, tenant isolation, input validation (`src/security.py`),
prompt-injection defense, output checks, audit logs, rate limiting, retention/deletion
controls, human approval for employment decisions.

## Scalability

CDN/WAF → Load Balancer → API Gateway → stateless Kubernetes services → Redis + PostgreSQL +
Qdrant → async queue → GPU inference cluster. Horizontal scaling and caching reduce latency.
The Human Escalation Desk scales as a lightweight ticket queue that can later route to a
distributed expert workforce across time zones for true 24-hour global coverage.

## Training

Start with RAG. Collect consented/anonymized feedback and resolved-escalation transcripts
(a direct source of "the AI didn't know this, but a human did") to prioritize knowledge-base
growth and, later, LoRA/QLoRA fine-tuning where it provides clear value. Version models and
support rollback.

## Commercialization

Candidate Free/Pro (Skilled and Unskilled tiers), Recruiter seats, Business/Enterprise plans,
enterprise knowledge assistant, hiring workflow automation, and a pay-per-resolved-escalation
or subscription model for the Human Escalation Desk.

## Differentiation

Candidate (skilled + unskilled) + business in one product, local/open-source-first AI, an
explicit AI-first/human-backed trust model with a committed 24-hour response SLA, career-to-hiring
workflow, enterprise RAG, agentic orchestration, voice-first UX and analytics.

## MVP Limitation

Authentication, production vector DB, distributed services, GPU orchestration, real local
voice, and a real staffed expert desk (currently a manual admin queue) are roadmap items
rather than hidden claims of completion.
