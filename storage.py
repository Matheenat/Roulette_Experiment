import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

DB_PATH = os.environ.get("DB_PATH", "game.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id    TEXT PRIMARY KEY,
    started_at    TEXT NOT NULL,
    ended_at      TEXT,
    start_balance INTEGER NOT NULL,
    wheel_type    TEXT NOT NULL DEFAULT 'european',
    stage         TEXT NOT NULL,
    odds_before   TEXT,
    odds_after    TEXT,
    ended_by      TEXT,
    history_views INTEGER NOT NULL DEFAULT 0,
    consent_given INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS rounds (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id       TEXT NOT NULL REFERENCES sessions(session_id),
    round_no         INTEGER NOT NULL,
    balance_before   INTEGER NOT NULL,
    bet_amount       INTEGER NOT NULL,
    bet_type         TEXT NOT NULL,
    pocket           INTEGER NOT NULL,
    result_color     TEXT NOT NULL,
    win              INTEGER NOT NULL,
    payout           INTEGER NOT NULL,
    balance_after    INTEGER NOT NULL,
    decision_seconds REAL,
    timestamp        TEXT NOT NULL,
    UNIQUE (session_id, round_no)
);
"""

ROUND_COLUMNS = ("round_no", "balance_before", "bet_amount", "bet_type",
                 "pocket", "result_color", "win", "payout", "balance_after",
                 "decision_seconds", "timestamp")

def now():
    return datetime.now(timezone.utc).isoformat()

@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with db() as conn:
        conn.executescript(SCHEMA)

def create_session(session_id, odds_before, start_balance):
    with db() as conn:
        conn.execute(
            "INSERT INTO sessions (session_id, started_at, start_balance, "
            "stage, odds_before, consent_given) VALUES (?, ?, ?, 'game', ?, 1)",
            (session_id, now(), start_balance, odds_before),
        )

def get_session(session_id):
    if not session_id:
        return None
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
    return dict(row) if row else None

def get_rounds(session_id):
    with db() as conn:
        rows = conn.execute(
            f"SELECT {', '.join(ROUND_COLUMNS)} FROM rounds "
            "WHERE session_id = ? ORDER BY round_no",
            (session_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def save_round(session_id, r):
    """Raises sqlite3.IntegrityError if (session_id, round_no) already exists."""
    with db() as conn:
        conn.execute(
            f"INSERT INTO rounds (session_id, {', '.join(ROUND_COLUMNS)}) "
            f"VALUES (?, {', '.join('?' for _ in ROUND_COLUMNS)})",
            (session_id, *(r[c] for c in ROUND_COLUMNS)),
        )

def end_play(session_id, ended_by):
    """The player stopped or went bust; the final question comes next."""
    with db() as conn:
        conn.execute(
            "UPDATE sessions SET stage = 'post', ended_by = ? "
            "WHERE session_id = ?",
            (ended_by, session_id),
        )

def finish_session(session_id, odds_after):
    with db() as conn:
        conn.execute(
            "UPDATE sessions SET stage = 'reveal', odds_after = ?, "
            "ended_at = ? WHERE session_id = ?",
            (odds_after, now(), session_id),
        )

def add_history_view(session_id):
    with db() as conn:
        conn.execute(
            "UPDATE sessions SET history_views = history_views + 1 "
            "WHERE session_id = ?",
            (session_id,),
        )