"""Data models for the ATS application."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParsedJobDescription:
    """Structured representation of an analyzed job description."""

    raw_text: str
    title: str
    required_skills: list[str]
    experience_required: float
    cleaned_text: str


@dataclass
class ParsedResume:
    """Structured information extracted from a candidate resume."""

    filename: str
    raw_text: str
    name: str
    email: str
    phone: str
    skills: list[str]
    education: list[str]
    experience_years: float
    current_company: str
    certifications: list[str]
    cleaned_text: str
    quality_score: float = 0.0
    skill_score: float = 0.0
    experience_score: float = 0.0
    education_score: float = 0.0
    certification_score: float = 0.0
    tfidf_score: float = 0.0
    ats_score: float = 0.0
    missing_skills: list[str] = field(default_factory=list)
    matched_skills: list[str] = field(default_factory=list)
    skill_recommendations: list[str] = field(default_factory=list)
    interview_questions: list[str] = field(default_factory=list)
    match_verdict: str = ""
    match_summary: str = ""
    match_reasoning: list[str] = field(default_factory=list)
    candidate_id: Optional[int] = None


@dataclass
class ScreeningResult:
    """Complete output of a screening run."""

    job: ParsedJobDescription
    candidates: list[ParsedResume]
    duplicate_pairs: list[tuple[str, str, float]] = field(default_factory=list)
