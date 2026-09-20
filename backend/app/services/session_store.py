"""
Conversation memory.

SQLite is used deliberately: the reviewer can open the file, inspect the schema
and see exactly what the system remembers. Three tables:

  sessions(id, title, created_at, updated_at, context_json, asked_slots_json, meta_json)
  messages(id, session_id, turn, role, content, payload_json, created_at)
  retrieval_log(id, session_id, turn, query, doc_id, score, created_at)

`asked_slots` is the anti-repetition ledger: once the assistant has asked for a
variable, that slot is recorded forever for the session and is never asked again,
whether or not the user answered. Unanswered slots become stated assumptions
instead of repeated questions.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..config import settings

_LOCK = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id              TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL,
    context_json    TEXT NOT NULL DEFAULT '{}',
    asked_slots_json TEXT NOT NULL DEFAULT '[]',
    meta_json       TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    turn        INTEGER NOT NULL,
    role        TEXT NOT NULL,
    content     TEXT NOT NULL,
    payload_json TEXT,
    created_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, turn);
CREATE TABLE IF NOT EXISTS retrieval_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,
    turn        INTEGER NOT NULL,
    query       TEXT NOT NULL,
    doc_id      TEXT NOT NULL,
    score       REAL NOT NULL,
    created_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_retrieval_session ON retrieval_log(session_id);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with _LOCK, _connect() as conn:
        conn.executescript(SCHEMA)


class SessionStore:
    # ------------------------------------------------------------------ create/read
    def create(self, title: str = "New analysis") -> str:
        session_id = uuid.uuid4().hex[:12]
        now = _now()
        with _LOCK, _connect() as conn:
            conn.execute(
                "INSERT INTO sessions (id, title, created_at, updated_at) VALUES (?,?,?,?)",
                (session_id, title, now, now),
            )
        return session_id

    def ensure(self, session_id: Optional[str]) -> str:
        if session_id:
            with _LOCK, _connect() as conn:
                row = conn.execute("SELECT id FROM sessions WHERE id=?", (session_id,)).fetchone()
            if row:
                return session_id
        return self.create()

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        with _LOCK, _connect() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
            if not row:
                return None
            messages = conn.execute(
                "SELECT turn, role, content, payload_json, created_at FROM messages "
                "WHERE session_id=? ORDER BY turn ASC, id ASC",
                (session_id,),
            ).fetchall()
        return {
            "id": row["id"],
            "title": row["title"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "context": json.loads(row["context_json"]),
            "asked_slots": json.loads(row["asked_slots_json"]),
            "meta": json.loads(row["meta_json"]),
            "messages": [
                {
                    "turn": m["turn"],
                    "role": m["role"],
                    "content": m["content"],
                    "payload": json.loads(m["payload_json"]) if m["payload_json"] else None,
                    "created_at": m["created_at"],
                }
                for m in messages
            ],
        }

    def list(self, limit: int = 40) -> List[Dict[str, Any]]:
        with _LOCK, _connect() as conn:
            rows = conn.execute(
                "SELECT s.*, (SELECT COUNT(*) FROM messages m WHERE m.session_id=s.id AND m.role='user') AS turns "
                "FROM sessions s ORDER BY datetime(s.updated_at) DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "id": r["id"],
                "title": r["title"],
                "created_at": r["created_at"],
                "updated_at": r["updated_at"],
                "turns": r["turns"],
                "context": json.loads(r["context_json"]),
            }
            for r in rows
        ]

    def delete(self, session_id: str) -> None:
        with _LOCK, _connect() as conn:
            conn.execute("DELETE FROM messages WHERE session_id=?", (session_id,))
            conn.execute("DELETE FROM retrieval_log WHERE session_id=?", (session_id,))
            conn.execute("DELETE FROM sessions WHERE id=?", (session_id,))

    # ------------------------------------------------------------------ update
    def save_context(self, session_id: str, context: Dict[str, Any]) -> None:
        with _LOCK, _connect() as conn:
            conn.execute(
                "UPDATE sessions SET context_json=?, updated_at=? WHERE id=?",
                (json.dumps(context), _now(), session_id),
            )

    def mark_asked(self, session_id: str, slots: List[str]) -> None:
        if not slots:
            return
        with _LOCK, _connect() as conn:
            row = conn.execute(
                "SELECT asked_slots_json FROM sessions WHERE id=?", (session_id,)
            ).fetchone()
            current = json.loads(row["asked_slots_json"]) if row else []
            merged = list(dict.fromkeys([*current, *slots]))
            conn.execute(
                "UPDATE sessions SET asked_slots_json=?, updated_at=? WHERE id=?",
                (json.dumps(merged), _now(), session_id),
            )

    def set_title(self, session_id: str, title: str) -> None:
        with _LOCK, _connect() as conn:
            conn.execute(
                "UPDATE sessions SET title=?, updated_at=? WHERE id=?",
                (title[:70], _now(), session_id),
            )

    def next_turn(self, session_id: str) -> int:
        with _LOCK, _connect() as conn:
            row = conn.execute(
                "SELECT COALESCE(MAX(turn), 0) AS t FROM messages WHERE session_id=?", (session_id,)
            ).fetchone()
        return int(row["t"]) + 1

    def add_message(
        self,
        session_id: str,
        turn: int,
        role: str,
        content: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        with _LOCK, _connect() as conn:
            conn.execute(
                "INSERT INTO messages (session_id, turn, role, content, payload_json, created_at) "
                "VALUES (?,?,?,?,?,?)",
                (session_id, turn, role, content, json.dumps(payload) if payload else None, _now()),
            )
            conn.execute("UPDATE sessions SET updated_at=? WHERE id=?", (_now(), session_id))

    def log_retrieval(self, session_id: str, turn: int, query: str, hits: List[Dict[str, Any]]) -> None:
        if not hits:
            return
        with _LOCK, _connect() as conn:
            conn.executemany(
                "INSERT INTO retrieval_log (session_id, turn, query, doc_id, score, created_at) "
                "VALUES (?,?,?,?,?,?)",
                [(session_id, turn, query, h["id"], h["score"], _now()) for h in hits],
            )

    def cited_docs(self, session_id: str) -> List[str]:
        with _LOCK, _connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT doc_id FROM retrieval_log WHERE session_id=?", (session_id,)
            ).fetchall()
        return [r["doc_id"] for r in rows]

    def history(self, session_id: str, limit: int = 12) -> List[Dict[str, str]]:
        with _LOCK, _connect() as conn:
            rows = conn.execute(
                "SELECT role, content FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?",
                (session_id, limit),
            ).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


store = SessionStore()
