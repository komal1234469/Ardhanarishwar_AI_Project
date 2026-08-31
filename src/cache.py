import hashlib
import redis

_client = None
_checked = False


def get_client(host="localhost", port=6379, db=0):
    """Lazily connect to Redis once. If Redis isn't running, cache is simply
    skipped everywhere (app keeps working without it)."""
    global _client, _checked
    if _checked:
        return _client
    _checked = True
    try:
        c = redis.Redis(host=host, port=port, db=db, socket_connect_timeout=1)
        c.ping()
        _client = c
    except Exception:
        _client = None
    return _client


def make_key(mode, user_type, text):
    """Same question (case/space-insensitive) + same mode/user_type -> same
    cache key, so repeated questions hit the cache instead of the model."""
    normalized = " ".join(text.lower().strip().split())
    raw = f"{mode}|{user_type}|{normalized}"
    return "ardhanarishwar:" + hashlib.sha256(raw.encode()).hexdigest()


def get_cached(mode, user_type, text):
    client = get_client()
    if not client:
        return None
    try:
        val = client.get(make_key(mode, user_type, text))
        return val.decode("utf-8") if val else None
    except Exception:
        return None


def set_cached(mode, user_type, text, answer, ttl_seconds=60 * 60 * 24 * 7):
    """Cache for 7 days by default (career/business advice doesn't go stale fast)."""
    client = get_client()
    if not client or not answer:
        return
    try:
        client.setex(make_key(mode, user_type, text), ttl_seconds, answer)
    except Exception:
        pass
