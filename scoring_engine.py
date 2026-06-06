"""ATS composite scoring engine with weighted parameters."""

from config import (
    CERTIFICATION_WEIGHT,
    EDUCATION_WEIGHT,
    EXPERIENCE_WEIGHT,
    SKILL_TAXONOMY,
    SKILL_WEIGHT,
)
from models import ParsedJobDescription, ParsedResume
from nlp_pipeline import extract_skills_from_text


def _enrich_skills(candidate: ParsedResume) -> None:
    """
    Re-extract skills from raw resume text to improve match accuracy.

    Args:
        candidate: Candidate record to enrich in place.
    """
    from_text = extract_skills_from_text(candidate.raw_text, SKILL_TAXONOMY)
    merged = {s.lower() for s in candidate.skills}
    merged.update(from_text)
    candidate.skills = sorted(merged)


def compute_skill_score(
    candidate_skills: list[str],
    required_skills: list[str],
    tfidf_score: float,
) -> float:
    """
    Compute skill match score blending keyword overlap, penalties, and TF-IDF.

    Args:
        candidate_skills: Skills extracted from the resume.
        required_skills: Skills required by the job description.
        tfidf_score: TF-IDF cosine similarity percentage.

    Returns:
        Skill score between 0 and 100.
    """
    if not required_skills:
        return round(max(tfidf_score, len(candidate_skills) * 8), 1)

    candidate_set = {s.lower() for s in candidate_skills}
    required_set = {s.lower() for s in required_skills}
    overlap = candidate_set & required_set
    match_ratio = len(overlap) / len(required_set)
    keyword_score = match_ratio * 100

    missing_penalty = max(0, (len(required_set) - len(overlap)) * 6)
    bonus = min(len(overlap) * 4, 20)

    blended = 0.55 * keyword_score + 0.25 * tfidf_score + 0.20 * bonus
    return round(max(0.0, min(blended - missing_penalty * 0.3, 100.0)), 1)


def compute_experience_score(candidate_years: float, required_years: float) -> float:
    """
    Score candidate experience against job requirements.

    Args:
        candidate_years: Years of experience on the resume.
        required_years: Minimum years required by the JD.

    Returns:
        Experience score between 0 and 100.
    """
    if required_years <= 0:
        return round(min(25.0 + candidate_years * 18.0, 100.0), 1)

    if candidate_years >= required_years:
        excess = min(candidate_years - required_years, 5)
        return round(min(85.0 + excess * 3, 100.0), 1)

    ratio = candidate_years / required_years
    return round(ratio * 75.0, 1)


def compute_education_score(education: list[str], job: ParsedJobDescription) -> float:
    """
    Score candidate education based on degree presence and relevance.

    Args:
        education: List of education entries from the resume.
        job: Parsed job description for context.

    Returns:
        Education score between 0 and 100.
    """
    if not education:
        return 20.0

    text = " ".join(education).lower()
    score = 40.0
    if any(kw in text for kw in ("bachelor", "b.tech", "b.e", "b.sc", "bca", "bba")):
        score += 30.0
    if any(kw in text for kw in ("master", "m.tech", "m.e", "m.sc", "mca", "mba")):
        score += 20.0
    if any(kw in text for kw in ("computer", "information technology", "software", "engineering")):
        score += 10.0
    if "education" in job.raw_text.lower() and score >= 70:
        score += 5.0
    return min(round(score, 1), 100.0)


def compute_certification_score(
    certifications: list[str],
    required_skills: list[str],
) -> float:
    """
    Score certifications relevance to the job requirements.

    Args:
        certifications: Certifications found on the resume.
        required_skills: Required skills from the job description.

    Returns:
        Certification score between 0 and 100.
    """
    if not certifications:
        return 15.0

    cert_text = " ".join(certifications).lower()
    relevant = sum(1 for skill in required_skills if skill.lower() in cert_text)
    base = min(len(certifications) * 18, 55)
    relevance = (relevant / max(len(required_skills), 1)) * 45
    return min(round(base + relevance, 1), 100.0)


def compute_ats_score(
    skill_score: float,
    experience_score: float,
    education_score: float,
    certification_score: float,
    quality_score: float = 0.0,
) -> float:
    """
    Compute weighted composite ATS score with a quality tiebreaker.

    Formula:
        ATS = 0.50*Skill + 0.20*Experience + 0.15*Education + 0.15*Certification
        (+ up to 5 pts quality bonus)

    Args:
        skill_score: Skill match component score.
        experience_score: Experience match component score.
        education_score: Education component score.
        certification_score: Certification component score.
        quality_score: Resume completeness score (0–100).

    Returns:
        Composite ATS score between 0 and 100.
    """
    base = (
        SKILL_WEIGHT * skill_score
        + EXPERIENCE_WEIGHT * experience_score
        + EDUCATION_WEIGHT * education_score
        + CERTIFICATION_WEIGHT * certification_score
    )
    quality_bonus = min(quality_score * 0.05, 5.0)
    return round(min(base + quality_bonus, 100.0), 1)


def score_candidate(
    candidate: ParsedResume,
    job: ParsedJobDescription,
    tfidf_score: float,
) -> ParsedResume:
    """
    Apply full ATS scoring pipeline to a parsed candidate.

    Args:
        candidate: Parsed resume object to score.
        job: Parsed job description.
        tfidf_score: Pre-computed TF-IDF similarity score.

    Returns:
        Updated ParsedResume with all score fields populated.
    """
    _enrich_skills(candidate)

    candidate.tfidf_score = tfidf_score
    candidate.skill_score = compute_skill_score(candidate.skills, job.required_skills, tfidf_score)
    candidate.experience_score = compute_experience_score(
        candidate.experience_years, job.experience_required
    )
    candidate.education_score = compute_education_score(candidate.education, job)
    candidate.certification_score = compute_certification_score(
        candidate.certifications, job.required_skills
    )
    candidate.ats_score = compute_ats_score(
        candidate.skill_score,
        candidate.experience_score,
        candidate.education_score,
        candidate.certification_score,
        candidate.quality_score,
    )
    return candidate
