import tempfile
import streamlit as st


@st.cache_resource
def load_stt_model():
    """Loads once per app session. 'tiny' model (~75MB) — small enough for
    CPU-only laptops, transcribes a few seconds of speech in ~1-2 sec."""
    from faster_whisper import WhisperModel
    return WhisperModel("tiny", device="cpu", compute_type="int8")


def transcribe_audio_bytes(audio_bytes):
    """Takes raw WAV bytes (from the mic recorder widget) and returns the
    transcribed text using a fully local model — no cloud/third-party STT."""
    if not audio_bytes:
        return ""
    model = load_stt_model()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        path = f.name
    segments, _ = model.transcribe(path, language="en")
    return " ".join(seg.text.strip() for seg in segments).strip()
