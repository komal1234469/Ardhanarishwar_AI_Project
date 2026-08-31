# Ardhanarishwar — A Global AI-First, Human-Backed Career & Business Platform

Local/open-source-first AI SaaS prototype for Recruweb. No OpenAI, Gemini, Anthropic or other paid AI API key is used.

## Positioning

Ardhanarishwar is not "just a chatbot." It is a **three-sided problem-solving platform**:

1. **Skilled candidates** — gap analysis against a target role and a personalized roadmap to better opportunities.
2. **Unskilled / first-time job seekers** — step-by-step, practical, foundational training toward job readiness (global vision: serve both skilled and unskilled populations).
3. **Businesses / clients** — AI-first answers to real-world business problems (e.g. declining sales, finding B2B clients), with automatic **escalation to a human expert team within 24 hours** whenever the AI isn't confident enough to answer reliably.

This "AI-first, human-backed" model is the core differentiator: the platform never pretends to know everything — low-confidence answers are queued for a real person instead of being guessed.

## Features
- Candidate (Skilled / Unskilled tracks) + Business modes
- Local LLM through optional Ollama
- Local RAG knowledge base
- Career advisor, resume analyzer, interview lab
- Recruitment/business assistant
- **Human Escalation Desk** — low-confidence queries are queued with the question, mode, candidate type and AI confidence score, for expert follow-up
- SQLite conversation memory, feedback and escalation log
- Admin analytics
- Browser voice UX (documented production path)
- Production architecture for Agentic AI, local STT/TTS and scalable global SaaS

## Run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Optional local GenAI:
```bash
ollama pull llama3.2:3b
```
The app still works without Ollama using a local deterministic assistant, and low-confidence
queries are automatically escalated to the Human Escalation Desk (Admin tab).

## Important
This is a functional MVP/prototype. Production authentication, distributed infrastructure, GPU orchestration and real local Whisper/Piper voice are documented as the next phase.
