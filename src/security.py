import re

def sanitize_text(text, max_chars=6000):
    text = (text or "").strip()
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return text[:max_chars]

def detect_prompt_injection(text):
    patterns = [
        r"ignore\s+(all|previous|prior)\s+instructions",
        r"reveal\s+(your|the)\s+(system|developer)\s+prompt",
        r"show\s+me\s+the\s+hidden\s+prompt",
        r"bypass\s+(security|policy|rules)"
    ]
    return any(re.search(p, text, re.I) for p in patterns)
