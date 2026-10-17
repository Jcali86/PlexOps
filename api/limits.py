"""Spending limits for the language model.

The request page takes free text from anyone the library is shared with, and
every mood search costs a fraction of a cent. Small numbers multiply: a bored
teenager holding down a button, a page left refreshing, or someone deciding to
see whether it will write their homework.

Three guards, in order of how much they matter:

  The model can only ever return filters. Structured output means the reply is
  a set of genres and thresholds, not free text, so it cannot be talked into
  writing an essay or a website however the request is phrased.

  Each person gets an hourly and a daily allowance.

  The whole server gets a daily ceiling, so no combination of people can run
  up a bill while the owner is asleep.
"""

from config import config

DEFAULTS = {"per_hour": 30, "per_day": 100, "server_per_day": 400, "max_query_chars": 200}


def limits():
    configured = (config.get("app") or {}).get("limits") or {}
    return {**DEFAULTS, **configured}


def ensure_table(db):
    db.conn.executescript("""
        CREATE TABLE IF NOT EXISTS ai_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plex_user_id TEXT NOT NULL,
            username TEXT,
            kind TEXT NOT NULL,
            used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_ai_usage_user ON ai_usage (plex_user_id, used_at);
        CREATE INDEX IF NOT EXISTS idx_ai_usage_at ON ai_usage (used_at);
    """)
    db.conn.commit()


def check(db, user):
    """May this person make another model call? Returns (ok, message, remaining)."""
    ensure_table(db)
    rule = limits()
    uid = str(user["id"])

    hour = db.conn.execute(
        "SELECT COUNT(*) FROM ai_usage WHERE plex_user_id = ? AND used_at > datetime('now', '-1 hour')",
        (uid,),
    ).fetchone()[0]
    if hour >= rule["per_hour"]:
        return False, "You have made a lot of searches in the last hour. Try again shortly.", 0

    day = db.conn.execute(
        "SELECT COUNT(*) FROM ai_usage WHERE plex_user_id = ? AND used_at > datetime('now', '-1 day')",
        (uid,),
    ).fetchone()[0]
    if day >= rule["per_day"]:
        return False, "That is today's searching done. It resets tomorrow.", 0

    everyone = db.conn.execute(
        "SELECT COUNT(*) FROM ai_usage WHERE used_at > datetime('now', '-1 day')"
    ).fetchone()[0]
    if everyone >= rule["server_per_day"]:
        return False, "Everyone has been busy today - searching is paused until tomorrow.", 0

    return True, "", rule["per_day"] - day


def record(db, user, kind="search"):
    """Take one from someone's allowance. Returns a handle for giving it back."""
    ensure_table(db)
    cursor = db.conn.execute(
        "INSERT INTO ai_usage (plex_user_id, username, kind) VALUES (?, ?, ?)",
        (str(user["id"]), user.get("username", ""), kind),
    )
    db.conn.commit()
    return cursor.lastrowid


def refund(db, usage_id):
    """Give an allowance back when the model turned out not to be needed."""
    if not usage_id:
        return
    ensure_table(db)
    db.conn.execute("DELETE FROM ai_usage WHERE id = ?", (usage_id,))
    db.conn.commit()


def clean_query(text):
    """Trim a request to something sane before it reaches the model."""
    query = " ".join((text or "").split())
    return query[: limits()["max_query_chars"]]
