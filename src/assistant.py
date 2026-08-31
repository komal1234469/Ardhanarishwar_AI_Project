from .security import sanitize_text, detect_prompt_injection
from .llm import ollama_available, generate_local, generate_local_stream
from .cache import get_cached, set_cached

# Keywords that mark a question as within this platform's actual scope
# (career/business/recruitment). Anything with none of these is treated as
# out-of-scope, even if a local LLM is running and technically "could"
# answer it from general knowledge — we don't want the assistant answering
# weather, recipes, general trivia, etc. as if it were an expert on them.
import re

# We block only CLEARLY off-topic categories (weather, recipes, entertainment,
# sports, jokes, general trivia) — everything else defaults to in-scope.
# A positive whitelist of "allowed" keywords doesn't scale: there are
# thousands of legitimate skill/tech/education terms (e.g. "propagation",
# "gradient descent", "overfitting") that no fixed list could ever cover,
# and blocking them wrongly denies real learning questions. A short
# blacklist of obviously-unrelated topics is far more reliable.
OUT_OF_SCOPE_KEYWORDS = [
    "weather", "temperature outside", "rain forecast", "climate today",
    "recipe", "cook ", "cooking", "how to cook", "restaurant near",
    "movie", "film review", "song lyrics", "music video", "actor", "actress",
    "cricket score", "football score", "match score", "ipl", "world cup score",
    "joke", "riddle", "funny story",
    "celebrity", "horoscope", "astrology", "zodiac sign",
    "capital of", "population of",
    "election result", "prime minister of", "president of",
    # common Hinglish/Hindi equivalents
    "mausam", "baarish", "khana banane", "recipe banao", "chutkula",
]

def is_in_scope(text):
    t = text.lower()
    return not any(kw in t for kw in OUT_OF_SCOPE_KEYWORDS)

OUT_OF_SCOPE_MESSAGE = (
    "Hmm, that's not something I can help with directly — I'm focused on career, jobs, "
    "resumes, interviews, skills, training, recruitment and business questions. "
    "I've sent it to our human team, and they'll find the answer and respond within "
    "**4 working days**. In the meantime, is there anything career or business related "
    "I can help you with?"
)

# Below this retrieval-confidence threshold, and when no local LLM is
# available to reason further, we treat the AI as "not confident enough"
# and escalate to a human expert instead of guessing.
ESCALATION_CONFIDENCE_THRESHOLD = 0.06

ESCALATION_MESSAGE = (
    "Hmm, that's not something I can answer confidently right now. "
    "I've sent it to our human team, and they'll find the answer and respond within **4 working days**. "
    "In the meantime, here's my best general guidance:\n\n"
)


class Ardhanarishwar:
    def __init__(self, rag, model="llama3.2:3b"):
        self.rag, self.model = rag, model

    def fallback(self, text, mode, user_type="Skilled"):
        t = text.lower()
        if "resume" in t or "cv" in t:
            return "Resume focus: target role, quantified achievements, relevant keywords, strong projects, and concise structure."
        if "interview" in t:
            return "Interview plan: introduction → technical questions → project deep-dive → behavioral questions → mock round with scoring."
        if "career" in t or "skill" in t or "job" in t:
            if mode == "Candidate" and user_type == "Unskilled":
                return ("Job-readiness plan: identify a beginner-friendly target role → learn foundational/vocational "
                        "skills step-by-step → practice with guided exercises → build one small real-world task as proof "
                        "of skill → apply for entry-level or apprenticeship roles → keep upskilling on the job.")
            return "Career plan: choose target role → map required skills → identify top gaps → build projects → prepare resume → practice interviews."
        if mode == "Business":
            return "Business workflow: requirement → role/skill extraction → screening criteria → interview rubric → human review → outcome analytics."
        return "I can help with career, jobs, resume, interviews, skills, education, training, recruitment and business questions."

    def answer(self, text, mode, history, user_type="Skilled", session_id=None, escalate_fn=None):
        text = sanitize_text(text)
        if not text:
            return "Please enter a question."
        if detect_prompt_injection(text):
            return "I can help with your request, but I cannot reveal hidden system instructions."

        cached = get_cached(mode, user_type, text)
        if cached:
            return cached

        docs = self.rag.retrieve(text, 3)
        context = "\n\n".join(d for d, _ in docs)
        best_score = max((s for _, s in docs), default=0.0)
        has_llm = ollama_available()

        # Out-of-scope only when BOTH signals say so: no scope keyword match
        # AND weak knowledge-base relevance. This avoids wrongly blocking
        # legitimate questions (e.g. basic math for the Unskilled/numeracy
        # track) that don't happen to contain a career-specific keyword but
        # do match the knowledge base.
        if not is_in_scope(text) and best_score < ESCALATION_CONFIDENCE_THRESHOLD:
            if escalate_fn and session_id:
                escalate_fn(session_id, mode, user_type, text, best_score)
            return OUT_OF_SCOPE_MESSAGE

        # AI-first, human-escalation-when-needed: if retrieval confidence is
        # low AND no local generative model is available to reason beyond
        # the knowledge base, don't guess — hand off to a human expert.
        if best_score < ESCALATION_CONFIDENCE_THRESHOLD and not has_llm:
            if escalate_fn and session_id:
                escalate_fn(session_id, mode, user_type, text, best_score)
            return ESCALATION_MESSAGE + self.fallback(text, mode, user_type)

        if has_llm:
            hist = "\n".join(f"{r}: {m}" for r, m in history[-8:])
            audience_note = (
                f"User type: {user_type} (tailor depth and vocabulary accordingly)."
                if mode == "Candidate" else ""
            )
            prompt = f'''You are Ardhanarishwar, a professional AI assistant for Recruweb.
Mode: {mode}. {audience_note} Be practical and structured. Do not make autonomous employment decisions.
Knowledge:
{context}
Conversation:
{hist}
User:
{text}
Answer helpfully.'''
            try:
                result = generate_local(prompt, self.model)
                set_cached(mode, user_type, text, result)
                return result
            except Exception:
                pass

        return self.fallback(text, mode, user_type)

    def analyze_resume(self, resume_text, target_role):
        """Role-aware resume analysis using the local LLM (skills present,
        gaps for that specific role, suggestions). Falls back to a simple
        generic scan only if no local model is available."""
        resume_text = sanitize_text(resume_text)
        target_role = sanitize_text(target_role) or "the target role"
        if not resume_text:
            return "Please paste a resume to analyze."

        cache_key_text = f"[resume]{target_role}::{resume_text[:500]}"
        cached = get_cached("ResumeAnalysis", target_role, cache_key_text)
        if cached:
            return cached

        if ollama_available():
            prompt = f'''You are a resume reviewer. Target role: {target_role}.
Resume:
{resume_text[:3000]}

Analyze this resume specifically for the "{target_role}" role. Respond in this exact structure:
**Detected relevant skills:** (skills in the resume relevant to this role)
**Potential gaps:** (skills/experience this role typically needs but the resume doesn't show)
**Suggestion:** (one concrete, specific improvement for this resume and this role)'''
            try:
                result = generate_local(prompt, self.model, num_predict=250)
                set_cached("ResumeAnalysis", target_role, cache_key_text, result)
                return result
            except Exception:
                pass

        # Fallback (no LLM running): generic keyword scan, clearly labeled as such
        skills = ["python", "sql", "aws", "excel", "communication", "leadership",
                  "project management", "data analysis", "customer service"]
        t = resume_text.lower()
        found = [s for s in skills if s in t]
        missing = [s for s in skills if s not in t]
        return (f"(Generic scan — start Ollama for role-specific analysis)\n\n"
                f"**Detected skills:** {', '.join(found) or 'None'}\n"
                f"**Potential gaps:** {', '.join(missing) or 'None'}\n"
                f"**Suggestion:** Tailor keywords and quantified achievements to the \"{target_role}\" role specifically.")

    def generate_interview_questions(self, role, level, count=5, avoid=None, variation=0):
        """Role+level-aware interview questions via the local LLM. `avoid`
        is a list of already-asked questions (so a 'generate more' call
        doesn't repeat them). Falls back to a generic set only if no local
        model is available."""
        role = sanitize_text(role) or "the target role"
        level = sanitize_text(level) or "Fresher"
        avoid = avoid or []

        cache_key_text = f"[interview]{role}::{level}::{count}::v{variation}"
        cached = get_cached("InterviewLab", role, cache_key_text)
        if cached:
            return [q.strip("- ").strip() for q in cached.split("\n") if q.strip()]

        if ollama_available():
            avoid_note = ""
            if avoid:
                avoid_list = "\n".join(f"- {q}" for q in avoid[:15])
                avoid_note = f"\nDo NOT repeat or closely rephrase any of these already-asked questions:\n{avoid_list}\n"
            prompt = f'''Generate exactly {count} interview questions for a "{level}" level candidate applying for the "{role}" role.
Mix background/experience, role-specific technical/domain, and behavioral questions.
{avoid_note}
Output ONLY the {count} questions, one per line, no numbering, no extra text.'''
            try:
                result = generate_local(prompt, self.model, num_predict=60 * count)
                lines = [q.strip("- 0123456789.").strip() for q in result.split("\n") if q.strip()]
                lines = [q for q in lines if len(q) > 8][:count]
                if len(lines) >= max(3, count // 2):
                    set_cached("InterviewLab", role, cache_key_text, "\n".join(lines))
                    return lines
            except Exception:
                pass

        # Fallback (no LLM running): generic role-templated questions, extended pool
        pool = [
            f"Explain one project or experience relevant to the {role} role.",
            f"What core skills or tools does a {role} need, and how strong are you in them?",
            f"Describe a challenge you faced in work related to {role} and how you solved it.",
            f"Why are you interested in the {role} role specifically?",
            "How do you handle feedback or criticism at work?",
            f"Walk me through how you'd approach a typical day-one task as a {role}.",
            "Describe a time you worked under a tight deadline. What did you do?",
            f"What's a recent trend or change in the {role} field that you're aware of?",
            "How do you prioritize when you have multiple tasks at once?",
            "Tell me about a time you made a mistake at work and how you handled it.",
            f"How would you explain your value as a {role} candidate to a hiring manager?",
            "Describe a situation where you had to work with a difficult team member.",
        ]
        pool = [q for q in pool if q not in (avoid or [])]
        return pool[:count]

    def _build_prompt(self, text, mode, history, user_type, context):
        hist = "\n".join(f"{r}: {m}" for r, m in history[-8:])
        audience_note = (
            f"User type: {user_type} (tailor depth and vocabulary accordingly)."
            if mode == "Candidate" else ""
        )
        return f'''You are Ardhanarishwar, a professional AI assistant for Recruweb.
Mode: {mode}. {audience_note} Be practical and structured. Do not make autonomous employment decisions.
Knowledge:
{context}
Conversation:
{hist}
User:
{text}
Answer helpfully.'''

    def answer_stream(self, text, mode, history, user_type="Skilled", session_id=None, escalate_fn=None):
        """Same logic as answer(), but yields chunks as they're generated so
        the UI can render them live (st.write_stream). Falls back to yielding
        the full fallback/escalation text in one shot when no local LLM is
        available."""
        text = sanitize_text(text)
        if not text:
            yield "Please enter a question."
            return
        if detect_prompt_injection(text):
            yield "I can help with your request, but I cannot reveal hidden system instructions."
            return

        cached = get_cached(mode, user_type, text)
        if cached:
            yield cached
            return

        docs = self.rag.retrieve(text, 3)
        context = "\n\n".join(d for d, _ in docs)
        best_score = max((s for _, s in docs), default=0.0)
        has_llm = ollama_available()

        if not is_in_scope(text) and best_score < ESCALATION_CONFIDENCE_THRESHOLD:
            if escalate_fn and session_id:
                escalate_fn(session_id, mode, user_type, text, best_score)
            yield OUT_OF_SCOPE_MESSAGE
            return

        if best_score < ESCALATION_CONFIDENCE_THRESHOLD and not has_llm:
            if escalate_fn and session_id:
                escalate_fn(session_id, mode, user_type, text, best_score)
            yield ESCALATION_MESSAGE + self.fallback(text, mode, user_type)
            return

        if has_llm:
            prompt = self._build_prompt(text, mode, history, user_type, context)
            try:
                got_any = False
                full = []
                for piece in generate_local_stream(prompt, self.model):
                    got_any = True
                    full.append(piece)
                    yield piece
                if got_any:
                    set_cached(mode, user_type, text, "".join(full))
                    return
            except Exception:
                pass

        yield self.fallback(text, mode, user_type)
