"""Job description parsing and structured requirement extraction."""

import re
from typing import List

from config import SKILL_TAXONOMY
from models import ParsedJobDescription
from nlp_pipeline import clean_text, extract_skills_from_text


def extract_experience_requirement(text: str) -> float:
    """
    Extract minimum years of experience from a job description.

    Args:
        text: Raw job description text.

    Returns:
        Required years of experience as a float (0 if not found).
    """
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)",
        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)",
        r"minimum\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
    ]
    text_lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return float(match.group(1))
    return 0.0


def extract_job_title(text: str) -> str:
    """
    Extract a job title from the first meaningful line of the JD.

    Args:
        text: Raw job description text.

    Returns:
        Detected job title or a default label.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return "Job Opening"

    title = lines[0]
    if len(title) > 80:
        title = title[:80]
    return title


def parse_job_description(raw_text: str) -> ParsedJobDescription:
    """
    Parse a job description into structured requirements.

    Args:
        raw_text: Raw job description text pasted by the recruiter.

    Returns:
        ParsedJobDescription with skills, experience, and cleaned text.
    """
    required_skills = extract_skills_from_text(raw_text, SKILL_TAXONOMY)

    skills_section = re.search(
        r"(?:required\s+skills?|skills?\s+required|must\s+have|qualifications?)\s*[:\-]?\s*(.+?)(?:\n\n|\n[A-Z]|$)",
        raw_text,
        re.IGNORECASE | re.DOTALL,
    )
    if skills_section:
        section_skills = extract_skills_from_text(skills_section.group(1), SKILL_TAXONOMY)
        for skill in section_skills:
            if skill not in required_skills:
                required_skills.append(skill)

    comma_skills = re.findall(
        r"(?:required\s+skills?|skills?\s*[:\-]\s*)([^\n]+)",
        raw_text,
        re.IGNORECASE,
    )
    known_set = set(SKILL_TAXONOMY)
    for block in comma_skills:
        for token in re.split(r"[,;/|]", block):
            token_clean = re.sub(r"\s+", " ", token.strip().lower())
            if token_clean in known_set and token_clean not in required_skills:
                required_skills.append(token_clean)

    return ParsedJobDescription(
        raw_text=raw_text,
        title=extract_job_title(raw_text),
        required_skills=sorted(set(required_skills)),
        experience_required=extract_experience_requirement(raw_text),
        cleaned_text=clean_text(raw_text),
    )
