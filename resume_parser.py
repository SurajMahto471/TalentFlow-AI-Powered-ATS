"""Resume parsing engine for structured information extraction."""

import re
from typing import List

import spacy

from config import CERTIFICATION_KEYWORDS, DEGREE_PATTERNS, SKILL_TAXONOMY
from document_extractor import extract_candidate_name_from_filename
from models import ParsedResume
from nlp_pipeline import clean_text, extract_skills_from_text

_nlp = spacy.load("en_core_web_sm")


def extract_email(text: str) -> str:
    """
    Extract the first email address from text.

    Args:
        text: Raw resume text.

    Returns:
        Email address or empty string.
    """
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    """
    Extract a phone number from text.

    Args:
        text: Raw resume text.

    Returns:
        Phone number string or empty string.
    """
    patterns = [
        r"\+?\d{1,3}[\s\-]?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{4}",
        r"\b\d{10}\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return ""


def extract_name(text: str, filename: str) -> str:
    """
    Extract candidate name using spaCy NER with filename fallback.

    Args:
        text: Raw resume text.
        filename: Uploaded filename for fallback parsing.

    Returns:
        Detected candidate name.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    header = " ".join(lines[:5])
    doc = _nlp(header)

    for ent in doc.ents:
        if ent.label_ == "PERSON" and len(ent.text.split()) <= 4:
            return ent.text.title()

    for line in lines[:3]:
        if re.match(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}$", line):
            return line

    return extract_candidate_name_from_filename(filename)


def extract_education(text: str) -> List[str]:
    """
    Extract education entries from resume text.

    Args:
        text: Raw resume text.

    Returns:
        List of education strings (degree + institution hints).
    """
    education: list[str] = []
    text_lower = text.lower()
    lines = text.splitlines()

    for line in lines:
        line_lower = line.lower().strip()
        for pattern in DEGREE_PATTERNS:
            if re.search(pattern, line_lower):
                cleaned = line.strip()
                if cleaned and cleaned not in education:
                    education.append(cleaned)
                break

    uni_pattern = r"(?:university|college|institute|iit|nit|bits|vit|srm)\s+[\w\s,]+"
    for match in re.finditer(uni_pattern, text_lower):
        snippet = match.group(0).title()
        if snippet not in education:
            education.append(snippet)

    return education[:5]


def extract_experience_years(text: str) -> float:
    """
    Estimate total years of experience from resume text.

    Args:
        text: Raw resume text.

    Returns:
        Estimated years of experience.
    """
    text_lower = text.lower()
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)",
        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)",
        r"total\s+experience\s*[:\-]?\s*(\d+(?:\.\d+)?)",
    ]
    years_found: list[float] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text_lower):
            years_found.append(float(match.group(1)))

    if years_found:
        return max(years_found)

    year_ranges = re.findall(r"(20\d{2})\s*[-–]\s*(20\d{2}|present|current)", text_lower)
    if year_ranges:
        from datetime import datetime
        current_year = datetime.now().year
        total = 0.0
        for start, end in year_ranges:
            end_year = current_year if end in ("present", "current") else int(end)
            total += max(0, end_year - int(start))
        return min(total, 40.0)

    return 0.0


def extract_current_company(text: str) -> str:
    """
    Extract the current or most recent company name.

    Args:
        text: Raw resume text.

    Returns:
        Company name or empty string.
    """
    patterns = [
        r"(?:currently at|working at|employed at|present\s*[:\-]\s*)\s*([A-Z][A-Za-z0-9\s&.,]+)",
        r"(?:company|organization)\s*[:\-]\s*([A-Z][A-Za-z0-9\s&.,]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            company = match.group(1).strip().split("\n")[0][:60]
            return company

    exp_section = re.search(
        r"(?:experience|work history|employment)(.+?)(?:education|skills|projects|$)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if exp_section:
        lines = [l.strip() for l in exp_section.group(1).splitlines() if l.strip()]
        for line in lines[:5]:
            if re.match(r"^[A-Z]", line) and len(line) < 60:
                return line

    return ""


def extract_certifications(text: str) -> List[str]:
    """
    Extract certifications from resume text.

    Args:
        text: Raw resume text.

    Returns:
        List of detected certification names.
    """
    text_lower = text.lower()
    found: list[str] = []

    for cert in CERTIFICATION_KEYWORDS:
        if cert in text_lower:
            found.append(cert.title())

    cert_section = re.search(
        r"certifications?\s*[:\-]?\s*(.+?)(?:\n\n|skills|projects|education|$)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if cert_section:
        for line in cert_section.group(1).splitlines():
            line = line.strip().lstrip("•-* ")
            if line and len(line) < 80:
                found.append(line)

    return list(dict.fromkeys(found))[:10]


def parse_resume(raw_text: str, filename: str) -> ParsedResume:
    """
    Parse a resume into structured candidate information.

    Args:
        raw_text: Extracted raw text from the resume document.
        filename: Original uploaded filename.

    Returns:
        ParsedResume with extracted fields populated.
    """
    skills = extract_skills_from_text(raw_text, SKILL_TAXONOMY)

    skills_section = re.search(
        r"(?:skills?|technical skills?|core competencies)\s*[:\-]?\s*(.+?)(?:\n\n|experience|education|projects|$)",
        raw_text,
        re.IGNORECASE | re.DOTALL,
    )
    if skills_section:
        section_skills = extract_skills_from_text(skills_section.group(1), SKILL_TAXONOMY)
        for skill in section_skills:
            if skill not in skills:
                skills.append(skill)

    return ParsedResume(
        filename=filename,
        raw_text=raw_text,
        name=extract_name(raw_text, filename),
        email=extract_email(raw_text),
        phone=extract_phone(raw_text),
        skills=sorted(set(skills)),
        education=extract_education(raw_text),
        experience_years=extract_experience_years(raw_text),
        current_company=extract_current_company(raw_text),
        certifications=extract_certifications(raw_text),
        cleaned_text=clean_text(raw_text),
    )


def _merge_skills(existing: list[str], csv_skills: list[str]) -> list[str]:
    """
    Merge CSV-provided skills with taxonomy-extracted skills.

    Args:
        existing: Skills already extracted from resume text.
        csv_skills: Skills parsed from CSV columns.

    Returns:
        Deduplicated sorted skill list.
    """
    merged = {s.lower() for s in existing}
    for skill in csv_skills:
        skill_lower = skill.lower()
        if skill_lower in SKILL_TAXONOMY:
            merged.add(skill_lower)
        else:
            for known in SKILL_TAXONOMY:
                if skill_lower in known or known in skill_lower:
                    merged.add(known)
                    break
            else:
                merged.add(skill_lower)
    return sorted(merged)


def parse_resume_from_csv(
    row: dict,
    filename: str,
    raw_text: str,
) -> ParsedResume:
    """
    Parse a candidate from a structured CSV row.

    Uses CSV column values where available and falls back to NLP extraction
    from synthesized resume text.

    Args:
        row: Normalized CSV row dictionary.
        filename: Display label for the candidate (e.g., ``candidates.csv — John``).
        raw_text: Text synthesized from the CSV row for NLP scoring.

    Returns:
        ParsedResume with CSV fields merged into NLP-extracted data.
    """
    candidate = parse_resume(raw_text, filename)

    if row.get("name"):
        candidate.name = str(row["name"]).strip().title()
    if row.get("email"):
        candidate.email = str(row["email"]).strip()
    if row.get("phone"):
        candidate.phone = str(row["phone"]).strip()
    if row.get("company"):
        candidate.current_company = str(row["company"]).strip()
    if row.get("skills"):
        csv_skills = []
        for item in str(row["skills"]).split(","):
            item = item.strip()
            if item:
                csv_skills.append(item)
        candidate.skills = _merge_skills(candidate.skills, csv_skills)
    if row.get("education"):
        edu = str(row["education"]).strip()
        if edu and edu not in candidate.education:
            candidate.education = [edu] + candidate.education
    if row.get("certifications"):
        for cert in str(row["certifications"]).split(","):
            cert = cert.strip()
            if cert and cert not in candidate.certifications:
                candidate.certifications.append(cert)
    if row.get("experience"):
        exp = _parse_csv_experience(row["experience"])
        if exp > 0:
            candidate.experience_years = exp

    candidate.raw_text = raw_text
    candidate.cleaned_text = clean_text(raw_text)
    return candidate


def _parse_csv_experience(value: object) -> float:
    """
    Parse experience value from a CSV cell.

    Args:
        value: Raw CSV cell value.

    Returns:
        Years of experience as a float.
    """
    match = re.search(r"(\d+(?:\.\d+)?)", str(value))
    return float(match.group(1)) if match else 0.0
