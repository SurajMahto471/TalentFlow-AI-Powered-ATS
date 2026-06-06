"""Skill gap analysis and learning recommendations."""

from config import SKILL_TAXONOMY
from models import ParsedJobDescription, ParsedResume

LEARNING_RECOMMENDATIONS: dict[str, str] = {
    "python": "Complete a Python fundamentals course and build 2-3 backend projects.",
    "java": "Study OOP in Java and practice Spring Boot microservice projects.",
    "sql": "Practice advanced SQL joins, window functions, and query optimization.",
    "docker": "Learn Docker basics and deploy a containerized web application.",
    "aws": "Prepare for AWS Cloud Practitioner or Solutions Architect Associate.",
    "azure": "Explore Azure fundamentals and deploy a sample app on Azure App Service.",
    "kubernetes": "Complete a CKA prep course and practice kubectl deployments.",
    "machine learning": "Build an end-to-end ML pipeline with scikit-learn or TensorFlow.",
    "react": "Build a React SPA with state management and API integration.",
    "django": "Create a full-stack Django REST API with authentication.",
    "flask": "Build a REST API with Flask and deploy it using Gunicorn.",
    "fastapi": "Develop an async FastAPI service with Pydantic validation.",
    "power bi": "Create interactive dashboards using Power BI Desktop.",
    "git": "Practice Git branching workflows and collaborative pull requests.",
}


def analyze_skill_gap(candidate: ParsedResume, job: ParsedJobDescription) -> ParsedResume:
    """
    Identify missing skills and generate learning recommendations.

    Args:
        candidate: Parsed candidate resume.
        job: Parsed job description with required skills.

    Returns:
        Updated candidate with missing_skills and skill_recommendations populated.
    """
    candidate_set = {s.lower() for s in candidate.skills}
    required_set = {s.lower() for s in job.required_skills}

    missing = sorted(required_set - candidate_set)
    candidate.missing_skills = missing

    recommendations: list[str] = []
    for skill in missing:
        rec = LEARNING_RECOMMENDATIONS.get(
            skill,
            f"Learn {skill.title()} through official documentation and a hands-on project.",
        )
        recommendations.append(rec)

    candidate.skill_recommendations = recommendations
    return candidate


def get_matched_skills(candidate: ParsedResume, job: ParsedJobDescription) -> list[str]:
    """
    Return skills that overlap between candidate and job requirements.

    Args:
        candidate: Parsed candidate resume.
        job: Parsed job description.

    Returns:
        List of matched skill names.
    """
    candidate_set = {s.lower() for s in candidate.skills}
    return [s for s in job.required_skills if s.lower() in candidate_set]
