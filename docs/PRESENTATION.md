# Ardhanarishwar — Presentation

### Slide 1 — Vision
A global AI-first, human-backed platform for career growth (skilled and unskilled candidates)
and real-world business problem solving.

### Slide 2 — Problem
**Candidate problem:** a gap between education/current skills and what target roles actually
require — this gap looks different for a skilled graduate vs. an unskilled first-time job
seeker, but both need a personalized path.
**Business problem:** business owners face real problems (declining sales, finding clients,
hiring) without instant access to expert guidance.

### Slide 3 — Solution
Candidate Mode (Skilled track + Unskilled track) + Business Mode + RAG + Local GenAI + Memory
+ Voice + Agentic AI + **AI-first, Human-backed Escalation** when the AI isn't confident.

### Slide 4 — Prototype
AI Assistant (dual candidate tracks + business mode), Resume Analyzer, Interview Lab, RAG
Knowledge Base, Human Escalation Desk, memory, feedback and analytics.

### Slide 5 — Architecture
UI → Router (mode + candidate type) → RAG → Local LLM or rule-based fallback → Confidence
check → Answer **or** Human Escalation → Memory + Audit Log.

### Slide 6 — API Independence
No paid third-party AI API keys. Local/open-source-first model strategy (optional Ollama).

### Slide 7 — Agentic AI
Specialized career, foundational-training (unskilled), resume, interview, learning,
recruitment, business and human-escalation agents with controlled tools.

### Slide 8 — The AI + Human Trust Model
AI always answers first. If retrieval confidence is low and no local LLM is available, the
question is queued for a human expert with a 24-hour response commitment — never a guessed
answer presented as certain.

### Slide 9 — Global Vision: Skilled + Unskilled
Skilled users: gap analysis and better career/business opportunities.
Unskilled users: personalized, practical, step-by-step training toward job readiness.
Same platform, two tailored paths — designed to scale to a global population.

### Slide 10 — Voice
Production: local Whisper STT → AI orchestration → local TTS.

### Slide 11 — Scale
Kubernetes, Redis, PostgreSQL, Qdrant, async queues, GPU inference, and a distributed human
expert desk for true 24-hour global coverage.

### Slide 12 — Security
RBAC, tenant isolation, encryption, audit logs, prompt-injection defense and human approval
for employment decisions.

### Slide 13 — Business Value
Candidate engagement across skill levels, recruiter productivity, enterprise knowledge, SaaS
revenue, and a trust advantage from never pretending the AI knows everything.

### Slide 14 — Roadmap
Voice → stronger vector search → agents → enterprise auth → integrations → evaluation →
staffed global escalation desk → multi-tenant SaaS.

### Slide 15 — Closing
Ardhanarishwar is more than a chatbot: it is an AI-first, human-backed career + recruitment +
business operating layer, built to serve skilled and unskilled people worldwide.
