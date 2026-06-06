"""CSV resume bulk upload parsing."""

import re
from io import BytesIO
from typing import Any, BinaryIO, Union

import pandas as pd

# Maps normalized field names to accepted CSV column headers
COLUMN_ALIASES: dict[str, list[str]] = {
    "name": ["name", "candidate_name", "full_name", "candidate", "applicant"],
    "email": ["email", "email_address", "mail", "e_mail"],
    "phone": ["phone", "mobile", "contact", "phone_number", "contact_number"],
    "skills": ["skills", "technical_skills", "key_skills", "skill_set", "core_skills"],
    "experience": ["experience", "years_of_experience", "experience_years", "total_experience", "exp"],
    "education": ["education", "degree", "qualification", "university", "college"],
    "certifications": ["certifications", "certification", "certs", "certificates"],
    "company": ["company", "current_company", "employer", "organization"],
    "resume_text": ["resume_text", "resume", "profile", "summary", "bio", "description", "about"],
}


def _normalize_column(column: str) -> str:
    """
    Map a CSV column header to a standard field name.

    Args:
        column: Raw column header from the CSV file.

    Returns:
        Normalized field name, or the lowercased original if unmatched.
    """
    cleaned = re.sub(r"[^a-z0-9_]", "_", column.strip().lower())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")

    for field, aliases in COLUMN_ALIASES.items():
        if cleaned in aliases:
            return field
    return cleaned


def _parse_list_value(value: Any) -> list[str]:
    """
    Parse a CSV cell into a list of strings.

    Args:
        value: Cell value (string, number, or empty).

    Returns:
        List of trimmed string tokens.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    text = str(value).strip()
    if not text:
        return []
    return [item.strip() for item in re.split(r"[,;|]", text) if item.strip()]


def _parse_experience_value(value: Any) -> float:
    """
    Extract numeric years of experience from a CSV cell.

    Args:
        value: Cell value such as ``3``, ``3.5``, or ``3 years``.

    Returns:
        Years of experience as a float, or 0.0 if not parseable.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0.0
    match = re.search(r"(\d+(?:\.\d+)?)", str(value))
    return float(match.group(1)) if match else 0.0


def build_resume_text_from_row(row: dict[str, Any]) -> str:
    """
    Build searchable resume text from structured CSV row data.

    Args:
        row: Normalized row dictionary from a CSV record.

    Returns:
        Multi-line text suitable for NLP parsing and scoring.
    """
    parts: list[str] = []

    if row.get("name"):
        parts.append(f"Name: {row['name']}")
    if row.get("email"):
        parts.append(f"Email: {row['email']}")
    if row.get("phone"):
        parts.append(f"Phone: {row['phone']}")
    if row.get("company"):
        parts.append(f"Current Company: {row['company']}")
    if row.get("experience"):
        parts.append(f"Experience: {row['experience']} years")
    if row.get("skills"):
        skills = _parse_list_value(row["skills"])
        parts.append(f"Skills: {', '.join(skills)}")
    if row.get("education"):
        parts.append(f"Education: {row['education']}")
    if row.get("certifications"):
        certs = _parse_list_value(row["certifications"])
        parts.append(f"Certifications: {', '.join(certs)}")
    if row.get("resume_text"):
        parts.append(str(row["resume_text"]))

    return "\n".join(parts).strip()


def parse_csv_candidates(
    uploaded_file: Union[BinaryIO, BytesIO],
    filename: str,
) -> list[tuple[str, str, dict[str, Any]]]:
    """
    Parse a CSV file into individual candidate records.

    Each row represents one candidate. Column headers are matched flexibly
    (e.g., ``candidate_name``, ``email_address``, ``technical_skills``).

    Args:
        uploaded_file: Uploaded CSV file object.
        filename: Original CSV filename.

    Returns:
        List of tuples: (candidate_label, raw_text, normalized_row_dict).
        Returns an empty list if parsing fails.
    """
    try:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
    except Exception:
        return []

    if df.empty:
        return []

    df.columns = [_normalize_column(str(col)) for col in df.columns]
    candidates: list[tuple[str, str, dict[str, Any]]] = []

    for index, row in df.iterrows():
        row_dict: dict[str, Any] = {}
        for col, value in row.items():
            if pd.isna(value):
                continue
            row_dict[col] = value

        if not row_dict:
            continue

        name = str(row_dict.get("name", f"Candidate {index + 1}")).strip()
        label = f"{filename} — {name}"
        raw_text = build_resume_text_from_row(row_dict)
        candidates.append((label, raw_text, row_dict))

    return candidates
