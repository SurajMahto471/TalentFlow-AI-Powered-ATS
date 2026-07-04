"""FastAPI backend for the AI-Powered Applicant Tracking System."""

import secrets
from io import BytesIO
from typing import Any, Optional

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import database
from auth import authenticate_user, get_user_profile, register_user, update_profile
from models import ParsedResume, ScreeningResult
from screening_service import run_screening

# In-memory session tokens (reset when the API restarts with a fresh database)
_sessions: dict[str, int] = {}

app = FastAPI(
    title="AI-Powered ATS API",
    description="Automated resume screening, scoring, and candidate ranking",
    version="1.0.0",
)

@app.get("/")
def root():
    return {"status": "AI-Powered ATS API is running", "docs": "/docs"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScreeningSummary(BaseModel):
    """Summary response after a screening run."""

    job_title: str
    required_skills: list[str]
    experience_required: float
    total_candidates: int
    top_candidate: Optional[str]
    top_ats_score: Optional[float]


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=1)
    email: str
    password: str = Field(..., min_length=6)
    phone: str = ""


class LoginRequest(BaseModel):
    email: str
    password: str


class ProfileUpdateRequest(BaseModel):
    full_name: str = Field(..., min_length=1)
    phone: str = ""


def _serialize_user(user: dict[str, Any]) -> dict[str, Any]:
    """Return a safe user payload without credentials."""
    return {
        "id": user["id"],
        "fullName": user["full_name"],
        "email": user["email"],
        "phone": user.get("phone", ""),
    }


def _create_session(user_id: int) -> str:
    """Create a new auth token for the given user."""
    token = secrets.token_urlsafe(32)
    _sessions[token] = user_id
    return token


def _get_user_from_token(authorization: Optional[str]) -> dict[str, Any]:
    """Resolve the current user from an Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.removeprefix("Bearer ").strip()
    user_id = _sessions.get(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    user = get_user_profile(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_current_user(authorization: Optional[str] = Header(None)) -> dict[str, Any]:
    """FastAPI dependency for protected routes."""
    return _get_user_from_token(authorization)


def _status_from_score(ats_score: float) -> str:
    """Map ATS score to recruiter status label."""
    if ats_score >= 75:
        return "Shortlisted"
    if ats_score >= 55:
        return "Interview"
    if ats_score >= 35:
        return "Review"
    return "Rejected"


def _serialize_candidate(candidate: ParsedResume, rank: int) -> dict[str, Any]:
    """Convert a ParsedResume to a JSON-serializable dict for the frontend."""
    return {
        "id": str(candidate.candidate_id or rank),
        "rank": rank,
        "name": candidate.name,
        "email": candidate.email,
        "phone": candidate.phone,
        "avatar": "".join(w[0] for w in candidate.name.split()[:2]).upper() or "NA",
        "atsScore": candidate.ats_score,
        "matchPercentage": round(candidate.skill_score, 1),
        "skillMatch": round(candidate.skill_score, 1),
        "qualityScore": round(candidate.quality_score, 1),
        "experience": candidate.experience_years,
        "skills": candidate.skills,
        "missingSkills": candidate.missing_skills,
        "matchedSkills": candidate.matched_skills,
        "status": _status_from_score(candidate.ats_score),
        "verdict": candidate.match_verdict,
        "recommendation": candidate.match_summary,
        "education": candidate.education,
        "certifications": candidate.certifications,
        "company": candidate.current_company,
        "resumeText": candidate.raw_text,
        "scoreBreakdown": {
            "skills": candidate.skill_score,
            "experience": candidate.experience_score,
            "education": candidate.education_score,
            "certifications": candidate.certification_score,
        },
        "reasoning": candidate.match_reasoning,
        "interviewQuestions": candidate.interview_questions,
        "filename": candidate.filename,
    }


def _serialize_db_candidate(row: dict[str, Any], rank: int) -> dict[str, Any]:
    """Convert a database candidate row to frontend JSON."""
    name = row.get("name") or "Unknown"
    ats_score = float(row.get("ats_score") or 0)
    skill_score = float(row.get("skill_score") or 0)
    return {
        "id": str(row["id"]),
        "rank": rank,
        "name": name,
        "email": row.get("email") or "",
        "phone": row.get("phone") or "",
        "avatar": "".join(w[0] for w in name.split()[:2]).upper() or "NA",
        "atsScore": ats_score,
        "matchPercentage": round(skill_score, 1),
        "skillMatch": round(skill_score, 1),
        "qualityScore": round(float(row.get("quality_score") or 0), 1),
        "experience": float(row.get("experience_years") or 0),
        "skills": row.get("skills") or [],
        "missingSkills": row.get("missing_skills") or [],
        "matchedSkills": row.get("matched_skills") or [],
        "status": _status_from_score(ats_score),
        "verdict": row.get("match_verdict") or "",
        "recommendation": row.get("match_summary") or "",
        "education": row.get("education") or [],
        "certifications": row.get("certifications") or [],
        "company": row.get("current_company") or "",
        "resumeText": row.get("raw_text") or "",
        "scoreBreakdown": {
            "skills": skill_score,
            "experience": float(row.get("experience_score") or 0),
            "education": float(row.get("education_score") or 0),
            "certifications": float(row.get("certification_score") or 0),
        },
        "reasoning": row.get("match_reasoning") or [],
        "interviewQuestions": row.get("interview_questions") or [],
        "filename": row.get("filename") or "",
    }


def _serialize_result(result: ScreeningResult) -> dict[str, Any]:
    """Serialize a full screening result for the React dashboard."""
    candidates = [
        _serialize_candidate(c, i + 1) for i, c in enumerate(result.candidates)
    ]
    scores = [c.ats_score for c in result.candidates]
    shortlisted = sum(1 for c in result.candidates if c.ats_score >= 75)
    rejected = sum(1 for c in result.candidates if c.ats_score < 35)

    return {
        "job": {
            "title": result.job.title,
            "rawText": result.job.raw_text,
            "requiredSkills": result.job.required_skills,
            "experienceRequired": result.job.experience_required,
        },
        "candidates": candidates,
        "duplicates": [
            {"fileA": a, "fileB": b, "similarity": s}
            for a, b, s in result.duplicate_pairs
        ],
        "stats": {
            "totalApplications": len(candidates),
            "shortlisted": shortlisted,
            "rejected": rejected,
            "avgAtsScore": round(sum(scores) / len(scores), 1) if scores else 0,
            "activeJobs": 1,
        },
    }


def _build_dashboard_payload(
    job: Optional[dict[str, Any]],
    candidates: list[dict[str, Any]],
    screening: Optional[dict[str, Any]],
    active_jobs: int,
) -> dict[str, Any]:
    """Build the dashboard response from user-scoped database rows."""
    if not job or not candidates:
        return {
            "hasResults": False,
            "job": None,
            "candidates": [],
            "duplicates": [],
            "stats": {
                "totalApplications": 0,
                "shortlisted": 0,
                "rejected": 0,
                "avgAtsScore": 0,
                "activeJobs": 0,
            },
        }

    serialized_candidates = [
        _serialize_db_candidate(c, i + 1) for i, c in enumerate(candidates)
    ]
    duplicates = screening.get("duplicate_pairs", []) if screening else []

    if screening:
        stats = {
            "totalApplications": screening.get("total_candidates", len(candidates)),
            "shortlisted": screening.get("shortlisted", 0),
            "rejected": screening.get("rejected", 0),
            "avgAtsScore": round(float(screening.get("avg_ats_score") or 0), 1),
            "activeJobs": active_jobs,
        }
    else:
        scores = [float(c.get("ats_score") or 0) for c in candidates]
        stats = {
            "totalApplications": len(candidates),
            "shortlisted": sum(1 for s in scores if s >= 75),
            "rejected": sum(1 for s in scores if s < 35),
            "avgAtsScore": round(sum(scores) / len(scores), 1) if scores else 0,
            "activeJobs": active_jobs,
        }

    return {
        "hasResults": True,
        "job": {
            "title": job.get("title") or "Job Description",
            "rawText": job.get("raw_text") or "",
            "requiredSkills": job.get("required_skills") or [],
            "experienceRequired": float(job.get("experience_required") or 0),
        },
        "candidates": serialized_candidates,
        "duplicates": duplicates,
        "stats": stats,
    }


@app.on_event("startup")
def startup() -> None:
    """Initialize database schema and clear in-memory sessions."""
    _sessions.clear()
    database.init_db()


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/auth/register")
def auth_register(body: RegisterRequest) -> dict[str, Any]:
    """Register a new recruiter account."""
    success, message = register_user(
        body.full_name, body.email, body.password, body.phone
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


@app.post("/auth/login")
def auth_login(body: LoginRequest) -> dict[str, Any]:
    """Authenticate and return a session token."""
    success, message, user = authenticate_user(body.email, body.password)
    if not success or not user:
        raise HTTPException(status_code=401, detail=message)
    token = _create_session(user["id"])
    return {"token": token, "user": _serialize_user(user), "message": message}


@app.get("/auth/me")
def auth_me(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    """Return the currently authenticated user."""
    return {"user": _serialize_user(user)}


@app.post("/auth/logout")
def auth_logout(authorization: Optional[str] = Header(None)) -> dict[str, str]:
    """Invalidate the current session token."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        _sessions.pop(token, None)
    return {"message": "Logged out"}


@app.put("/auth/profile")
def auth_update_profile(
    body: ProfileUpdateRequest,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Update the authenticated user's profile."""
    success, message = update_profile(user["id"], body.full_name, body.phone)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    refreshed = get_user_profile(user["id"])
    if not refreshed:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": _serialize_user(refreshed), "message": message}


@app.post("/screen")
async def screen_candidates(
    job_description: str = Form(...),
    resumes: list[UploadFile] = File(...),
    _user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Screen uploaded resumes against a job description.

    Returns full screening results for the React dashboard.
    """
    files = []
    for upload in resumes:
        content = await upload.read()
        files.append((upload.filename or "resume.pdf", BytesIO(content)))

    result = run_screening(job_description, files, persist=True, user_id=_user["id"])
    return _serialize_result(result)


@app.get("/dashboard")
def get_dashboard(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    """Return screening data scoped to the authenticated user."""
    user_id = user["id"]
    data = database.get_user_dashboard_data(user_id)
    active_jobs = database.count_user_jobs(user_id)
    return _build_dashboard_payload(
        data["job"],
        data["candidates"],
        data["screening"],
        active_jobs,
    )


@app.get("/candidates")
def list_candidates(
    job_id: Optional[int] = None,
    user: dict[str, Any] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """List screened candidates for the authenticated user."""
    rows = database.get_candidates_for_user(user["id"], job_id)
    return [_serialize_db_candidate(row, i + 1) for i, row in enumerate(rows)]


@app.get("/candidates/{candidate_id}")
def get_candidate(
    candidate_id: int,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Retrieve a single candidate owned by the authenticated user."""
    candidate = database.get_candidate_by_id(candidate_id, user["id"])
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return _serialize_db_candidate(candidate, 1)


@app.get("/jobs/latest")
def get_latest_job(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    """Retrieve the most recent job description for the authenticated user."""
    job = database.get_latest_job_for_user(user["id"])
    if not job:
        return {}
    return {
        "title": job.get("title"),
        "rawText": job.get("raw_text"),
        "requiredSkills": job.get("required_skills") or [],
        "experienceRequired": job.get("experience_required") or 0,
    }
