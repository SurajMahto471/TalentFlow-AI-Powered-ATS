"""SQLite persistence layer for candidates, jobs, and screening results."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generator, Optional

from config import DB_PATH
from models import ParsedJobDescription, ParsedResume


def _get_connection() -> sqlite3.Connection:
    """Create a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager yielding a database connection."""
    conn = _get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def reset_db() -> None:
    """Delete the existing database file and create fresh empty tables."""
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()


def _migrate_db(conn: sqlite3.Connection) -> None:
    """Add user-scoping columns to existing tables when upgrading."""
    job_cols = {row[1] for row in conn.execute("PRAGMA table_info(job_descriptions)").fetchall()}
    if job_cols and "user_id" not in job_cols:
        conn.execute("ALTER TABLE job_descriptions ADD COLUMN user_id INTEGER")

    candidate_cols = {row[1] for row in conn.execute("PRAGMA table_info(candidates)").fetchall()}
    for column, col_type in [
        ("user_id", "INTEGER"),
        ("match_verdict", "TEXT DEFAULT ''"),
        ("match_summary", "TEXT DEFAULT ''"),
        ("match_reasoning", "TEXT DEFAULT '[]'"),
        ("matched_skills", "TEXT DEFAULT '[]'"),
    ]:
        if candidate_cols and column not in candidate_cols:
            conn.execute(f"ALTER TABLE candidates ADD COLUMN {column} {col_type}")


def init_db() -> None:
    """Initialize database tables if they do not exist."""
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                phone TEXT DEFAULT '',
                profile_photo TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS job_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT,
                raw_text TEXT NOT NULL,
                required_skills TEXT,
                experience_required REAL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );

            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                name TEXT,
                email TEXT,
                phone TEXT,
                raw_text TEXT,
                skills TEXT,
                education TEXT,
                experience_years REAL,
                current_company TEXT,
                certifications TEXT,
                quality_score REAL,
                skill_score REAL,
                experience_score REAL,
                education_score REAL,
                certification_score REAL,
                tfidf_score REAL,
                ats_score REAL,
                missing_skills TEXT,
                matched_skills TEXT,
                skill_recommendations TEXT,
                interview_questions TEXT,
                match_verdict TEXT DEFAULT '',
                match_summary TEXT DEFAULT '',
                match_reasoning TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (job_id) REFERENCES job_descriptions (id)
            );

            CREATE TABLE IF NOT EXISTS screening_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                total_candidates INTEGER DEFAULT 0,
                avg_ats_score REAL DEFAULT 0,
                shortlisted INTEGER DEFAULT 0,
                rejected INTEGER DEFAULT 0,
                duplicate_pairs TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (job_id) REFERENCES job_descriptions (id)
            );
            """
        )
        _migrate_db(conn)


def save_job(job: ParsedJobDescription, user_id: int) -> int:
    """Persist a parsed job description scoped to a user."""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO job_descriptions (user_id, title, raw_text, required_skills, experience_required, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                job.title,
                job.raw_text,
                json.dumps(job.required_skills),
                job.experience_required,
                datetime.utcnow().isoformat(),
            ),
        )
        return int(cursor.lastrowid)


def save_candidate(job_id: int, candidate: ParsedResume, user_id: int) -> int:
    """Persist a screened candidate record scoped to a user."""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO candidates (
                user_id, job_id, filename, name, email, phone, raw_text, skills, education,
                experience_years, current_company, certifications, quality_score,
                skill_score, experience_score, education_score, certification_score,
                tfidf_score, ats_score, missing_skills, matched_skills, skill_recommendations,
                interview_questions, match_verdict, match_summary, match_reasoning, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                job_id,
                candidate.filename,
                candidate.name,
                candidate.email,
                candidate.phone,
                candidate.raw_text,
                json.dumps(candidate.skills),
                json.dumps(candidate.education),
                candidate.experience_years,
                candidate.current_company,
                json.dumps(candidate.certifications),
                candidate.quality_score,
                candidate.skill_score,
                candidate.experience_score,
                candidate.education_score,
                candidate.certification_score,
                candidate.tfidf_score,
                candidate.ats_score,
                json.dumps(candidate.missing_skills),
                json.dumps(candidate.matched_skills),
                json.dumps(candidate.skill_recommendations),
                json.dumps(candidate.interview_questions),
                candidate.match_verdict,
                candidate.match_summary,
                json.dumps(candidate.match_reasoning),
                datetime.utcnow().isoformat(),
            ),
        )
        return int(cursor.lastrowid)


def save_screening_result(
    user_id: int,
    job_id: int,
    total_candidates: int,
    avg_ats_score: float,
    shortlisted: int,
    rejected: int,
    duplicate_pairs: list[tuple[str, str, float]],
) -> int:
    """Persist analytics snapshot for a screening run."""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO screening_results (
                user_id, job_id, total_candidates, avg_ats_score, shortlisted, rejected,
                duplicate_pairs, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                job_id,
                total_candidates,
                avg_ats_score,
                shortlisted,
                rejected,
                json.dumps([{"fileA": a, "fileB": b, "similarity": s} for a, b, s in duplicate_pairs]),
                datetime.utcnow().isoformat(),
            ),
        )
        return int(cursor.lastrowid)


def get_latest_job_for_user(user_id: int) -> Optional[dict[str, Any]]:
    """Fetch the most recent job description for a user."""
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT * FROM job_descriptions
            WHERE user_id = ?
            ORDER BY id DESC LIMIT 1
            """,
            (user_id,),
        ).fetchone()
        if not row:
            return None
        data = dict(row)
        data["required_skills"] = json.loads(data["required_skills"] or "[]")
        return data


def get_candidates_for_user(user_id: int, job_id: Optional[int] = None) -> list[dict[str, Any]]:
    """Retrieve candidates for a user, optionally filtered by job."""
    query = "SELECT * FROM candidates WHERE user_id = ?"
    params: list[Any] = [user_id]
    if job_id is not None:
        query += " AND job_id = ?"
        params.append(job_id)
    query += " ORDER BY ats_score DESC"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
        return [_row_to_dict(row) for row in rows]


def get_candidate_by_id(candidate_id: int, user_id: int) -> Optional[dict[str, Any]]:
    """Fetch a single candidate owned by the given user."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM candidates WHERE id = ? AND user_id = ?",
            (candidate_id, user_id),
        ).fetchone()
        return _row_to_dict(row) if row else None


def get_latest_screening_for_user(user_id: int) -> Optional[dict[str, Any]]:
    """Fetch the latest screening analytics snapshot for a user."""
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT * FROM screening_results
            WHERE user_id = ?
            ORDER BY id DESC LIMIT 1
            """,
            (user_id,),
        ).fetchone()
        if not row:
            return None
        data = dict(row)
        data["duplicate_pairs"] = json.loads(data["duplicate_pairs"] or "[]")
        return data


def count_user_jobs(user_id: int) -> int:
    """Count job descriptions owned by a user."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS count FROM job_descriptions WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return int(row["count"]) if row else 0


def get_user_dashboard_data(user_id: int) -> dict[str, Any]:
    """Return job, candidates, and analytics for the user's latest screening."""
    job = get_latest_job_for_user(user_id)
    if not job:
        return {"job": None, "candidates": [], "screening": None}

    candidates = get_candidates_for_user(user_id, job["id"])
    screening = get_latest_screening_for_user(user_id)
    return {"job": job, "candidates": candidates, "screening": screening}


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    """Convert a SQLite row to a dictionary with JSON fields parsed."""
    data = dict(row)
    for field in (
        "skills", "education", "certifications", "missing_skills", "matched_skills",
        "skill_recommendations", "interview_questions", "match_reasoning",
    ):
        if field in data and isinstance(data[field], str):
            data[field] = json.loads(data[field] or "[]")
    return data


def save_user(
    full_name: str,
    email: str,
    password_hash: str,
    salt: str,
    phone: str = "",
) -> int:
    """Create a new user account."""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (full_name, email, password_hash, salt, phone, profile_photo, created_at)
            VALUES (?, ?, ?, ?, ?, '', ?)
            """,
            (full_name, email, password_hash, salt, phone, datetime.utcnow().isoformat()),
        )
        return int(cursor.lastrowid)


def get_user_by_email(email: str) -> Optional[dict[str, Any]]:
    """Fetch a user by email address."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[dict[str, Any]]:
    """Fetch a user by primary key."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def update_user_profile(
    user_id: int,
    full_name: str,
    phone: str,
    profile_photo: Optional[str] = None,
) -> None:
    """Update user profile fields."""
    with get_db() as conn:
        if profile_photo is not None:
            conn.execute(
                """
                UPDATE users SET full_name = ?, phone = ?, profile_photo = ?
                WHERE id = ?
                """,
                (full_name, phone, profile_photo, user_id),
            )
        else:
            conn.execute(
                """
                UPDATE users SET full_name = ?, phone = ?
                WHERE id = ?
                """,
                (full_name, phone, user_id),
            )
