"""Text preprocessing, vectorization, and similarity scoring for resume screening."""

import re
from typing import List

try:
    import spacy
except ImportError:  # pragma: no cover - behavior exercised in integration
    spacy = None
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_nlp = None
if spacy:
    try:
        _nlp = spacy.load("en_core_web_sm")
    except Exception:
        _nlp = None

# Minimal stop-word list used when spaCy is not available. Keep small to avoid
# adding heavy dependencies; sufficient for a temporary fallback tokenizer.
_FALLBACK_STOP_WORDS = {
    "a",
    "an",
    "and",
    "the",
    "or",
    "in",
    "on",
    "for",
    "to",
    "of",
    "with",
    "by",
    "is",
    "are",
    "was",
    "were",
    "it",
    "this",
    "that",
    "as",
    "be",
    "from",
}


def clean_text(text: str) -> str:
    """
    Normalize and clean raw text for NLP processing.

    Converts text to lowercase, removes URLs and email addresses, strips
    special punctuation, and removes standard English stop-words using spaCy.

    Args:
        text: Raw input text from a job description or resume.

    Returns:
        A cleaned, space-delimited string ready for vectorization.
    """
    if not text:
        return ""

    cleaned = text.lower()
    cleaned = re.sub(r"https?://\S+|www\.\S+", " ", cleaned)
    cleaned = re.sub(r"\S+@\S+\.\S+", " ", cleaned)
    cleaned = re.sub(r"[^a-z0-9\s/+.-]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if _nlp:
        doc = _nlp(cleaned)
        tokens = [
            token.text
            for token in doc
            if not token.is_stop and not token.is_space and token.text.strip()
        ]
    else:
        # Fallback simple tokenizer: split on whitespace and remove a small
        # set of common stop words and punctuation.
        parts = re.split(r"\s+", cleaned)
        tokens = [t for t in parts if t and t not in _FALLBACK_STOP_WORDS]

    result = " ".join(tokens)
    if not result and cleaned:
        result = cleaned
    return result


def _prepare_for_vectorization(texts: List[str]) -> List[str]:
    """
    Ensure each document has content suitable for TF-IDF vectorization.

    Args:
        texts: Raw or cleaned text documents.

    Returns:
        Documents guaranteed to contain at least one token each.
    """
    prepared: list[str] = []
    for text in texts:
        doc = (text or "").strip()
        if not doc:
            doc = "empty document"
        prepared.append(doc)
    return prepared


def _safe_tfidf_matrix(texts: List[str]):
    """
    Build a TF-IDF matrix, handling empty or stop-word-only documents.

    Args:
        texts: List of text documents to vectorize.

    Returns:
        Sparse TF-IDF matrix, or None if vectorization is not possible.
    """
    if not texts:
        return None

    prepared = _prepare_for_vectorization(texts)

    try:
        return TfidfVectorizer(
            stop_words=None,
            token_pattern=r"(?u)\b\w+\b",
            min_df=1,
        ).fit_transform(prepared)
    except ValueError:
        fallback = [
            re.sub(r"[^\w\s]", " ", t).lower() or f"document {i}"
            for i, t in enumerate(prepared)
        ]
        try:
            return TfidfVectorizer(
                stop_words=None,
                token_pattern=r"(?u)\b\w+\b",
                min_df=1,
            ).fit_transform(fallback)
        except ValueError:
            last_resort = [f"document token {i} {t}" for i, t in enumerate(fallback)]
            try:
                return TfidfVectorizer(
                    stop_words=None,
                    token_pattern=r"(?u)\b\w+\b",
                    min_df=1,
                ).fit_transform(last_resort)
            except ValueError:
                return None


def extract_skills_from_text(text: str, skill_taxonomy: List[str]) -> List[str]:
    """
    Match known skills from a skill taxonomy within raw text.

    Args:
        text: Text to scan for skills (resume or job description).
        skill_taxonomy: List of known skill keywords.

    Returns:
        List of matched skills in lowercase.
    """
    text_lower = text.lower()
    found: list[str] = []

    for skill in skill_taxonomy:
        pattern = r"\b" + re.escape(skill).replace(r"\ ", r"\s+") + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)

    return found


def _vectorization_text(raw_text: str, cleaned_text: str) -> str:
    """
    Build the best available text for TF-IDF vectorization.

    Args:
        raw_text: Original extracted document text.
        cleaned_text: NLP-cleaned text.

    Returns:
        Combined text prioritising raw content for richer vocabulary.
    """
    raw = (raw_text or "").strip()
    cleaned = (cleaned_text or "").strip()
    if raw and cleaned:
        return f"{raw} {cleaned}"
    return raw or cleaned or "empty document"


def compute_match_scores(job_description: str, resumes: List[str]) -> List[float]:
    """
    Compute TF-IDF cosine similarity between a job description and resumes.

    Args:
        job_description: Cleaned job description text.
        resumes: List of cleaned resume texts to compare against the job description.

    Returns:
        A list of similarity scores as percentages (e.g., 85.4), one per resume.
        Returns an empty list if no valid corpus is available.
    """
    if not job_description.strip() or not resumes:
        return []

    corpus = [job_description] + resumes

    if not any(doc.strip() for doc in corpus):
        return []

    tfidf_matrix = _safe_tfidf_matrix(corpus)
    if tfidf_matrix is None:
        return [0.0] * len(resumes)

    job_vector = tfidf_matrix[0:1]
    resume_vectors = tfidf_matrix[1:]

    similarities = cosine_similarity(job_vector, resume_vectors)[0]
    return [round(float(score) * 100, 1) for score in similarities]


def compute_pairwise_similarity(texts: List[str]) -> List[List[float]]:
    """
    Compute pairwise cosine similarity matrix for a list of texts.

    Args:
        texts: List of cleaned text documents.

    Returns:
        Square similarity matrix as nested lists.
    """
    if len(texts) < 2:
        return []

    matrix = _safe_tfidf_matrix(texts)
    if matrix is None:
        return [[0.0] * len(texts) for _ in texts]

    return cosine_similarity(matrix).tolist()
