"""Orchestrates the full ATS screening pipeline."""

from typing import BinaryIO, Optional, Union

from csv_extractor import parse_csv_candidates
from database import init_db, save_candidate, save_job, save_screening_result
from document_extractor import extract_text_from_document
from duplicate_detector import detect_duplicates
from interview_generator import attach_interview_questions
from jd_analyzer import parse_job_description
from models import ParsedResume, ScreeningResult
from nlp_pipeline import _vectorization_text, compute_match_scores
from quality_analyzer import attach_quality_score
from resume_parser import parse_resume, parse_resume_from_csv
from reasoning_engine import attach_reasoning
from scoring_engine import score_candidate
from skill_gap import analyze_skill_gap


def _is_csv_file(filename: str) -> bool:
    """Return True if the uploaded file is a CSV."""
    return filename.rsplit(".", 1)[-1].lower() == "csv"


def _load_candidates_from_file(
    filename: str,
    file_obj: Union[BinaryIO, bytes],
) -> list[ParsedResume]:
    """
    Load one or more candidates from a single uploaded file.

    CSV files expand to one candidate per row; PDF/DOCX yield a single candidate.

    Args:
        filename: Original uploaded filename.
        file_obj: File-like object or bytes buffer.

    Returns:
        List of parsed (but not yet scored) candidate records.
    """
    loaded: list[ParsedResume] = []

    if _is_csv_file(filename):
        csv_rows = parse_csv_candidates(file_obj, filename)
        for label, raw_text, row_dict in csv_rows:
            candidate = parse_resume_from_csv(row_dict, label, raw_text)
            loaded.append(attach_quality_score(candidate))
    else:
        raw_text = extract_text_from_document(file_obj, filename)
        candidate = parse_resume(raw_text, filename)
        loaded.append(attach_quality_score(candidate))

    return loaded


def run_screening(
    job_description_text: str,
    uploaded_files: list[tuple[str, Union[BinaryIO, bytes]]],
    persist: bool = True,
    user_id: Optional[int] = None,
) -> ScreeningResult:
    """
    Execute the complete ATS screening workflow.

    Args:
        job_description_text: Raw job description pasted by recruiter.
        uploaded_files: List of (filename, file_object) tuples.
        persist: Whether to save results to SQLite.
        user_id: Owner of the screening data (required when persist=True).

    Returns:
        ScreeningResult containing parsed job, ranked candidates, and duplicates.
    """
    init_db()
    job = parse_job_description(job_description_text)

    candidates: list[ParsedResume] = []
    vector_texts: list[str] = []

    for filename, file_obj in uploaded_files:
        for candidate in _load_candidates_from_file(filename, file_obj):
            candidates.append(candidate)
            vector_texts.append(_vectorization_text(candidate.raw_text, candidate.cleaned_text))

    job_vector_text = job.raw_text or job.cleaned_text
    tfidf_scores = compute_match_scores(job_vector_text, vector_texts)

    for i, candidate in enumerate(candidates):
        tfidf = tfidf_scores[i] if i < len(tfidf_scores) else 0.0
        score_candidate(candidate, job, tfidf)
        analyze_skill_gap(candidate, job)
        attach_interview_questions(candidate, job)
        attach_reasoning(candidate, job)

    candidates.sort(key=lambda c: c.ats_score, reverse=True)

    try:
        duplicates = detect_duplicates(candidates)
    except Exception:
        duplicates = []

    if persist and user_id is not None:
        job_id = save_job(job, user_id)
        for candidate in candidates:
            candidate.candidate_id = save_candidate(job_id, candidate, user_id)
        scores = [c.ats_score for c in candidates]
        shortlisted = sum(1 for c in candidates if c.ats_score >= 75)
        rejected = sum(1 for c in candidates if c.ats_score < 35)
        save_screening_result(
            user_id=user_id,
            job_id=job_id,
            total_candidates=len(candidates),
            avg_ats_score=round(sum(scores) / len(scores), 1) if scores else 0.0,
            shortlisted=shortlisted,
            rejected=rejected,
            duplicate_pairs=duplicates,
        )

    return ScreeningResult(job=job, candidates=candidates, duplicate_pairs=duplicates)
