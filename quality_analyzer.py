"""Resume quality analyzer for recruiter insights."""

import re

from models import ParsedResume

QUALITY_CHECKS: list[tuple[str, int]] = [
    ("email", 15),
    ("phone", 10),
    ("skills", 20),
    ("experience", 20),
    ("education", 15),
    ("certifications", 10),
    ("projects", 10),
]


def analyze_resume_quality(candidate: ParsedResume) -> float:
    """
    Compute a resume quality score out of 100.

    Checks for presence of email, phone, skills, experience, education,
    certifications, and project sections.

    Args:
        candidate: Parsed candidate resume.

    Returns:
        Quality score between 0 and 100.
    """
    score = 0
    text_lower = candidate.raw_text.lower()

    if candidate.email:
        score += 15
    if candidate.phone:
        score += 10
    if candidate.skills:
        score += 20
    if candidate.experience_years > 0 or "experience" in text_lower:
        score += 20
    if candidate.education:
        score += 15
    if candidate.certifications:
        score += 10
    if re.search(r"projects?\s*[:\-]", text_lower) or "project" in text_lower:
        score += 10

    return float(min(score, 100))


def get_quality_issues(candidate: ParsedResume) -> list[str]:
    """
    List specific quality issues found in a resume.

    Args:
        candidate: Parsed candidate resume.

    Returns:
        List of human-readable issue descriptions.
    """
    issues: list[str] = []
    text_lower = candidate.raw_text.lower()

    if not candidate.email:
        issues.append("Missing email address")
    if not candidate.phone:
        issues.append("Missing phone number")
    if not candidate.skills:
        issues.append("No skills detected")
    if candidate.experience_years <= 0 and "experience" not in text_lower:
        issues.append("No experience section detected")
    if not candidate.education:
        issues.append("No education details found")
    if not candidate.certifications:
        issues.append("No certifications listed")
    if "project" not in text_lower:
        issues.append("No projects section found")

    return issues


def attach_quality_score(candidate: ParsedResume) -> ParsedResume:
    """
    Compute and attach quality score to a candidate.

    Args:
        candidate: Parsed candidate resume.

    Returns:
        Updated candidate with quality_score populated.
    """
    candidate.quality_score = analyze_resume_quality(candidate)
    return candidate
