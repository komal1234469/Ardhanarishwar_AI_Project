import sqlite3
from datetime import datetime
from pathlib import Path

DB = Path("ardhanarishwar.db")

def init_db():
    con = sqlite3.connect(DB)
    con.execute('CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, message TEXT, created_at TEXT)')
    con.execute('CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, rating INTEGER, comment TEXT, created_at TEXT)')
    con.execute('''CREATE TABLE IF NOT EXISTS escalations(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        mode TEXT,
                        user_type TEXT,
                        question TEXT,
                        ai_confidence REAL,
                        status TEXT DEFAULT 'pending',
                        created_at TEXT,
                        resolved_at TEXT,
                        resolution TEXT)''')
    con.commit(); con.close()

def add_message(session_id, role, message):
    con = sqlite3.connect(DB)
    con.execute("INSERT INTO messages(session_id,role,message,created_at) VALUES(?,?,?,?)",
                (session_id, role, message, datetime.utcnow().isoformat()))
    con.commit(); con.close()

def history(session_id, limit=12):
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT role,message FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?",
                       (session_id, limit)).fetchall()
    con.close()
    return list(reversed(rows))

def add_feedback(session_id, rating, comment):
    con = sqlite3.connect(DB)
    con.execute("INSERT INTO feedback(session_id,rating,comment,created_at) VALUES(?,?,?,?)",
                (session_id, rating, comment, datetime.utcnow().isoformat()))
    con.commit(); con.close()

def add_escalation(session_id, mode, user_type, question, ai_confidence):
    con = sqlite3.connect(DB)
    con.execute("""INSERT INTO escalations(session_id,mode,user_type,question,ai_confidence,status,created_at)
                   VALUES(?,?,?,?,?,?,?)""",
                (session_id, mode, user_type, question, ai_confidence, "pending", datetime.utcnow().isoformat()))
    con.commit(); con.close()

def list_escalations(status=None, limit=50):
    con = sqlite3.connect(DB)
    if status:
        rows = con.execute("""SELECT id, session_id, mode, user_type, question, ai_confidence, status, created_at, resolution, resolved_at
                               FROM escalations WHERE status=? ORDER BY id DESC LIMIT ?""", (status, limit)).fetchall()
    else:
        rows = con.execute("""SELECT id, session_id, mode, user_type, question, ai_confidence, status, created_at, resolution, resolved_at
                               FROM escalations ORDER BY id DESC LIMIT ?""", (limit,)).fetchall()
    con.close()
    return rows

def resolve_escalation(escalation_id, resolution):
    con = sqlite3.connect(DB)
    con.execute("""UPDATE escalations SET status='resolved', resolved_at=?, resolution=? WHERE id=?""",
                (datetime.utcnow().isoformat(), resolution, escalation_id))
    con.commit(); con.close()

def metrics():
    con = sqlite3.connect(DB)
    users = con.execute("SELECT COUNT(DISTINCT session_id) FROM messages").fetchone()[0]
    messages = con.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    avg = con.execute("SELECT AVG(rating) FROM feedback").fetchone()[0]
    pending_escalations = con.execute("SELECT COUNT(*) FROM escalations WHERE status='pending'").fetchone()[0]
    con.close()
    return users, messages, round(avg or 0, 2), pending_escalations
