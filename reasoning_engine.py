"""Generate recruiter-friendly verdicts and match reasoning."""

from models import ParsedJobDescription, ParsedResume
from skill_gap import get_matched_skills

VERDICT_LEVELS: list[tuple[float, str, str]] = [
    (80.0, "Strong Match", "Highly recommended — schedule interview immediately."),
    (65.0, "Good Match", "Good fit — proceed to technical screening."),
    (45.0, "Moderate Match", "Partial fit — review skill gaps before deciding."),
    (25.0, "Weak Match", "Limited alignment — consider only if pipeline is thin."),
    (0.0, "Not Recommended", "Does not meet minimum role requirements."),
]


def classify_verdict(ats_score: float) -> tuple[str, str]:
    """
    Map an ATS score to a verdict label and one-line recommendation.

    Args:
        ats_score: Composite ATS score (0–100).

    Returns:
        Tuple of (verdict_label, recommendation_sentence).
    """
    for threshold, verdict, recommendation in VERDICT_LEVELS:
        if ats_score >= threshold:
            return verdict, recommendation
    return "Not Recommended", VERDICT_LEVELS[-1][2]


def build_match_reasoning(
    candidate: ParsedResume,
    job: ParsedJobDescription,
) -> list[str]:
    """
    Build human-readable bullet points explaining a candidate's score.

    Args:
        candidate: Scored candidate record.
        job: Parsed job description.

    Returns:
        List of reasoning strings for recruiter review.
    """
    reasons: list[str] = []
    matched = get_matched_skills(candidate, job)
    required_count = len(job.required_skills)

    if required_count:
        if matched:
            reasons.append(
                f"Matched {len(matched)}/{required_count} required skills: "
                f"{', '.join(s.title() for s in matched)}"
            )
        else:
            reasons.append(f"No required skills matched (0/{required_count}).")
        if candidate.missing_skills:
            reasons.append(
                f"Missing skills: {', '.join(s.title() for s in candidate.missing_skills)}"
            )
    elif candidate.skills:
        reasons.append(
            f"Detected skills: {', '.join(s.title() for s in candidate.skills[:8])}"
        )
    else:
        reasons.append("No skills detected in resume — parsing may have failed.")

    if job.experience_required > 0:
        if candidate.experience_years >= job.experience_required:
            reasons.append(
                f"Experience OK: {candidate.experience_years} yrs "
                f"(required {job.experience_required}+ yrs)"
            )
        else:
            gap = job.experience_required - candidate.experience_years
            reasons.append(
                f"Experience gap: {candidate.experience_years} yrs "
                f"vs {job.experience_required}+ yrs required ({gap:.1f} yr short)"
            )
    elif candidate.experience_years > 0:
        reasons.append(f"Total experience: {candidate.experience_years} years")

    if candidate.education:
        reasons.append(f"Education: {candidate.education[0]}")
    else:
        reasons.append("No education details found")

    if candidate.certifications:
        reasons.append(
            f"Certifications: {', '.join(candidate.certifications[:3])}"
        )

    reasons.append(
        f"Score breakdown — Skills: {candidate.skill_score}, "
        f"Experience: {candidate.experience_score}, "
        f"Education: {candidate.education_score}, "
        f"Certs: {candidate.certification_score}, "
        f"Text similarity: {candidate.tfidf_score}"
    )

    return reasons


def attach_reasoning(candidate: ParsedResume, job: ParsedJobDescription) -> ParsedResume:
    """
    Populate verdict and reasoning fields on a candidate.

    Args:
        candidate: Scored candidate record.
        job: Parsed job description.

    Returns:
        Updated candidate with match_verdict, match_summary, match_reasoning, matched_skills.
    """
    candidate.matched_skills = get_matched_skills(candidate, job)
    verdict, summary = classify_verdict(candidate.ats_score)
    candidate.match_verdict = verdict
    candidate.match_summary = summary
    candidate.match_reasoning = build_match_reasoning(candidate, job)
    return candidate
