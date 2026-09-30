from __future__ import annotations

from datetime import datetime, timezone
import sqlite3
from pathlib import Path
import uuid

from .models import AnswerResponse, ApprovalRecord


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ApprovalStore:
    def __init__(self, db_path: str | Path):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS approvals (
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    response_json TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    reviewer_note TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def _connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def create(self, question: str, response: AnswerResponse) -> str:
        approval_id = str(uuid.uuid4())
        now = utc_now()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO approvals VALUES (?, ?, ?, 'pending', NULL, ?, ?)",
                (approval_id, question, response.model_dump_json(), now, now),
            )
        return approval_id

    def list_pending(self) -> list[ApprovalRecord]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM approvals WHERE decision='pending' ORDER BY created_at").fetchall()
        return [ApprovalRecord(**dict(r)) for r in rows]

    def decide(self, approval_id: str, decision: str, reviewer_note: str | None) -> ApprovalRecord:
        now = utc_now()
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE approvals SET decision=?, reviewer_note=?, updated_at=? WHERE id=?",
                (decision, reviewer_note, now, approval_id),
            )
            if cur.rowcount == 0:
                raise KeyError(approval_id)
            row = conn.execute("SELECT * FROM approvals WHERE id=?", (approval_id,)).fetchone()
        return ApprovalRecord(**dict(row))
