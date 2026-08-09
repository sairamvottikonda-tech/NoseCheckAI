"""
SQLite persistence for NoseCheck.

Identity model (important, read before extending):
  There is no login system yet. Each browser gets an anonymous UUID in a
  session cookie (see ensure_session_id in app/__init__.py). That UUID is
  the "patient_id" used for History and Profile. Clearing cookies or
  switching devices loses access to that history -- a real limitation,
  not an oversight. Replace with real accounts before this holds anything
  sensitive in production.

  The clinician side uses a per-result SHARE CODE instead of a clinician
  login. Anyone with the code can view and add a note to that result.
  There is no access control beyond possessing the code -- sufficient for
  a first version, not secure authentication.
"""
import sqlite3
import secrets
import string
import json
import os
from datetime import datetime, timezone
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nosecheck.db")


def _now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                display_name TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                share_code TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL,
                deviation_score REAL,
                classification TEXT,
                offset_value REAL,
                yaw REAL,
                status TEXT,
                symptom_score REAL,
                combined_score REAL,
                combined_classification TEXT,
                symptom_answers TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clinician_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                share_code TEXT NOT NULL,
                note TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (share_code) REFERENCES results(share_code)
            )
        """)


def ensure_patient(patient_id: str):
    with get_db() as conn:
        row = conn.execute("SELECT 1 FROM patients WHERE patient_id = ?", (patient_id,)).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO patients (patient_id, created_at) VALUES (?, ?)",
                (patient_id, _now()),
            )


def set_display_name(patient_id: str, name: str):
    ensure_patient(patient_id)
    with get_db() as conn:
        conn.execute(
            "UPDATE patients SET display_name = ? WHERE patient_id = ?",
            (name.strip()[:60], patient_id),
        )


def _gen_share_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    part = lambda n: "".join(secrets.choice(alphabet) for _ in range(n))
    return f"NCK-{part(4)}-{part(2)}"


def save_photo_result(patient_id: str, photo_result: dict) -> str:
    """
    Saves the photo-only result immediately after /upload, before the
    questionnaire is completed. Returns the share code so the frontend
    can carry it through to /questionnaire for enrichment.
    """
    ensure_patient(patient_id)
    code = _gen_share_code()
    with get_db() as conn:
        conn.execute("""
            INSERT INTO results
                (patient_id, share_code, created_at, deviation_score, classification,
                 offset_value, yaw, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            patient_id, code, _now(),
            photo_result.get("deviation_score"),
            photo_result.get("classification"),
            photo_result.get("offset"),
            photo_result.get("yaw"),
            photo_result.get("status", "measured"),
        ))
    return code


def update_result_symptoms(share_code: str, symptom_score: float, combined_score: float,
                           combined_classification: str, symptom_answers: dict):
    with get_db() as conn:
        conn.execute("""
            UPDATE results
            SET symptom_score = ?, combined_score = ?, combined_classification = ?, symptom_answers = ?
            WHERE share_code = ?
        """, (symptom_score, combined_score, combined_classification,
              json.dumps(symptom_answers), share_code.strip().upper()))


def get_history(patient_id: str):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM results WHERE patient_id = ? ORDER BY created_at DESC",
            (patient_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_latest(patient_id: str):
    h = get_history(patient_id)
    return h[0] if h else None


def get_patient_stats(patient_id: str):
    with get_db() as conn:
        p = conn.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,)).fetchone()
        count = conn.execute(
            "SELECT COUNT(*) c FROM results WHERE patient_id = ? AND status = 'measured'",
            (patient_id,),
        ).fetchone()["c"]
        return {
            "created_at": p["created_at"] if p else None,
            "display_name": p["display_name"] if p else None,
            "screening_count": count,
        }


def get_result_by_code(share_code: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM results WHERE share_code = ?", (share_code.strip().upper(),)
        ).fetchone()
        return dict(row) if row else None


def get_notes(share_code: str):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM clinician_notes WHERE share_code = ? ORDER BY created_at ASC",
            (share_code.strip().upper(),),
        ).fetchall()
        return [dict(r) for r in rows]


def add_note(share_code: str, note: str):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO clinician_notes (share_code, note, created_at) VALUES (?, ?, ?)",
            (share_code.strip().upper(), note, _now()),
        )
