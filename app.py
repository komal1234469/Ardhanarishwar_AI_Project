import uuid
import streamlit as st
from streamlit_mic_recorder import mic_recorder
from src.database import init_db, add_message, history, add_feedback, add_escalation, list_escalations, resolve_escalation, metrics
from src.rag import LocalRAG
from src.assistant import Ardhanarishwar
from src.stt import transcribe_audio_bytes
from src.resume_reader import extract_pdf_text

st.set_page_config(page_title="Ardhanarishwar AI", page_icon="✦", layout="wide")
init_db()

@st.cache_resource
def load_engine():
    return Ardhanarishwar(LocalRAG())

engine = load_engine()
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "mode" not in st.session_state:
    st.session_state.mode = "Candidate"
if "user_type" not in st.session_state:
    st.session_state.user_type = "Skilled"

st.title("✦ Ardhanarishwar AI")
st.caption("A Global AI-First, Human-Backed Platform — Career Growth for Skilled & Unskilled Candidates + Real-World Problem Solving for Businesses")

with st.sidebar:
    st.header("Workspace")
    st.session_state.mode = st.radio("Assistant mode", ["Candidate", "Business"])
    if st.session_state.mode == "Candidate":
        st.session_state.user_type = st.radio(
            "Candidate type",
            ["Skilled", "Unskilled"],
            help="Skilled: has some existing skills, wants gap analysis & better opportunities. "
                 "Unskilled: starting from scratch, needs step-by-step foundational training."
        )
    st.text_input("Your name (demo)", key="demo_name")
    st.divider()
    st.write("**Modules**")
    st.write("Career Advisor\nInterview Coach\nResume Assistant\nSkill & Learning Advisor\nRecruitment Assistant\nBusiness Assistant\nHuman Escalation Desk")
    users, messages, avg, pending_esc = metrics()
    st.divider()
    st.metric("Demo sessions", users)
    st.metric("Messages", messages)
    st.metric("Avg feedback", avg)
    st.metric("Pending human escalations", pending_esc)
    st.info("No paid AI API key required. Ollama is optional. When AI confidence is low, the query is escalated to a human expert instead of guessing.")

tabs = st.tabs(["AI Assistant", "Resume Analyzer", "Interview Lab", "Knowledge Base", "Admin & Escalations"])

with tabs[0]:
    label = f"{st.session_state.mode} Assistant"
    if st.session_state.mode == "Candidate":
        label += f" — {st.session_state.user_type} track"
    st.subheader(label)
    for role, msg in history(st.session_state.session_id):
        with st.chat_message("user" if role == "user" else "assistant"):
            st.write(msg)

    mic_col, text_col = st.columns([1, 8])
    with mic_col:
        audio = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key="mic", format="wav")
    with text_col:
        typed_prompt = st.chat_input("Ask about career, jobs, resume, interviews, hiring, training or business...")

    prompt = typed_prompt
    if audio and audio.get("bytes") and audio.get("id") != st.session_state.get("last_audio_id"):
        st.session_state.last_audio_id = audio.get("id")
        with st.spinner("Transcribing..."):
            transcribed = transcribe_audio_bytes(audio["bytes"])
        if transcribed:
            prompt = transcribed

    if prompt:
        add_message(st.session_state.session_id, "user", prompt)
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            full_answer = st.write_stream(
                engine.answer_stream(
                    prompt,
                    st.session_state.mode,
                    history(st.session_state.session_id),
                    user_type=st.session_state.user_type,
                    session_id=st.session_state.session_id,
                    escalate_fn=add_escalation,
                )
            )
        add_message(st.session_state.session_id, "assistant", full_answer)
    st.caption("🎤 tap to speak, or type — both use the same local AI (local Whisper STT, no cloud speech API).")

with tabs[1]:
    st.subheader("Resume / CV Analyzer")
    upload_mode = st.radio("How would you like to provide your resume?", ["Paste text", "Upload PDF"], horizontal=True)

    resume = ""
    if upload_mode == "Upload PDF":
        uploaded_pdf = st.file_uploader("Upload resume (PDF)", type=["pdf"])
        if uploaded_pdf is not None:
            with st.spinner("Reading PDF..."):
                resume = extract_pdf_text(uploaded_pdf)
            if resume:
                st.success(f"Extracted {len(resume)} characters from PDF.")
                with st.expander("Preview extracted text"):
                    st.text(resume[:2000] + ("..." if len(resume) > 2000 else ""))
            else:
                st.warning("Couldn't extract text from this PDF — it may be a scanned image. Try 'Paste text' instead.")
    else:
        resume = st.text_area("Paste resume text", height=260)

    target = st.text_input("Target role", placeholder="e.g. AI Developer")
    if st.button("Analyze Resume"):
        if resume.strip():
            with st.spinner("Analyzing for this role..."):
                result = engine.analyze_resume(resume, target or "the target role")
            st.success("Analysis complete")
            st.write(f"**Target role:** {target or 'Not specified'}")
            st.markdown(result)
        else:
            st.warning("Provide a resume first (paste text or upload a PDF).")

with tabs[2]:
    st.subheader("Interview Lab")
    role = st.text_input("Role", "AI Developer")
    level = st.selectbox("Level", ["Fresher", "Junior", "Intermediate"])
    count = st.slider("Number of questions", 5, 15, 8)

    if "interview_questions" not in st.session_state:
        st.session_state.interview_questions = []
    if "interview_role_key" not in st.session_state:
        st.session_state.interview_role_key = None

    current_key = (role, level)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Mock Round"):
            with st.spinner("Generating questions for this role..."):
                st.session_state.interview_questions = engine.generate_interview_questions(role, level, count=count)
            st.session_state.interview_role_key = current_key
    with col2:
        if st.session_state.interview_questions and st.button("➕ Generate More (new, no repeats)"):
            with st.spinner("Generating more questions..."):
                more = engine.generate_interview_questions(
                    role, level, count=count,
                    avoid=st.session_state.interview_questions,
                    variation=len(st.session_state.interview_questions),
                )
            st.session_state.interview_questions += more

    if st.session_state.interview_questions and st.session_state.interview_role_key == current_key:
        for i, q in enumerate(st.session_state.interview_questions, 1):
            st.write(f"**Q{i}.** {q}")
        st.info(f"Level: {level}. Evaluate correctness, clarity, structure and business relevance.")

with tabs[3]:
    st.subheader("Local Knowledge Base / RAG")
    st.caption("This is the verified knowledge the AI retrieves from before answering — it doesn't just make things up. Try a search below to see what matches.")
    kb_query = st.text_input("Search the knowledge base", placeholder="e.g. unskilled candidate training, business escalation, resume")
    if not kb_query:
        kb_query = "recruitment career business training"
    results = engine.rag.retrieve(kb_query, 3)
    if not results:
        st.write("No matching knowledge found for this query.")
    for doc, score in results:
        st.write(f"**Relevance {score:.2f}**")
        st.write(doc)
        st.divider()

with tabs[4]:
    st.subheader("Feedback & Product Analytics")
    rating = st.slider("Rate assistant", 1, 5, 5)
    comment = st.text_area("Feedback")
    if st.button("Submit Feedback"):
        add_feedback(st.session_state.session_id, rating, comment)
        st.success("Feedback stored locally.")

    st.divider()
    st.subheader("🧑‍💼 Human Escalation Desk")
    st.caption(
        "When the AI isn't confident enough to answer reliably, the question is queued here "
        "for a human expert — an 'AI-first, human-backed' support model rather than the AI "
        "pretending to know everything."
    )

    all_rows = list_escalations(status=None, limit=200)
    pending_count = sum(1 for r in all_rows if r[6] == "pending")
    resolved_count = sum(1 for r in all_rows if r[6] == "resolved")

    m1, m2, m3 = st.columns(3)
    m1.metric("🔴 Pending", pending_count)
    m2.metric("🟢 Resolved", resolved_count)
    m3.metric("Total", len(all_rows))

    esc_filter = st.selectbox("Filter", ["pending", "resolved", "all"], index=0)
    rows = list_escalations(status=None if esc_filter == "all" else esc_filter)

    if not rows:
        st.info("No escalations in this view yet.")

    for r in rows:
        eid, sid, mode, utype, question, conf, status, created, resolution, resolved_at = r

        badge = "🔴 PENDING" if status == "pending" else "🟢 RESOLVED"
        confidence_pct = f"{conf * 100:.0f}%"

        with st.expander(f"{badge} · #{eid} · {mode} / {utype} · AI confidence {confidence_pct} · {created[:16].replace('T', ' ')}"):
            st.markdown(f"**❓ Question:**\n\n{question}")
            if status == "pending":
                st.warning("Awaiting human expert response.")
                resolution_input = st.text_area("✍️ Expert resolution", key=f"res_{eid}")
                if st.button("✅ Mark resolved", key=f"btn_{eid}"):
                    if resolution_input.strip():
                        resolve_escalation(eid, resolution_input)
                        st.rerun()
                    else:
                        st.error("Write a resolution before marking it resolved.")
            else:
                st.success(f"**✔️ Expert resolution:**\n\n{resolution or '(no resolution text saved)'}")
                if resolved_at:
                    st.caption(f"Resolved at {resolved_at[:16].replace('T', ' ')}")

    st.divider()
    st.markdown("### Production roadmap")
    st.write("Local Whisper STT + Piper TTS → multilingual embeddings + Qdrant → Agent tools + RBAC → PostgreSQL + Redis → Kubernetes → evaluation + human feedback → multi-tenant, global-scale SaaS serving both skilled and unskilled candidates worldwide.")
