"""Resume duplicate detection using cosine similarity."""

import re
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import DUPLICATE_SIMILARITY_THRESHOLD
from models import ParsedResume


def _safe_pairwise_matrix(texts: List[str]) -> List[List[float]] | None:
    """
    Compute a pairwise cosine similarity matrix with fallbacks for edge cases.

    Handles empty documents, stop-word-only text, and TF-IDF vocabulary errors
    without raising exceptions.

    Args:
        texts: List of resume text documents.

    Returns:
        Similarity matrix as nested lists, or None if comparison is not possible.
    """
    n = len(texts)
    if n < 2:
        return None

    vectorizer = TfidfVectorizer(
        stop_words=None,
        token_pattern=r"(?u)\b\w+\b",
        min_df=1,
    )

    attempts = [
        [(t or "").strip() or "empty document" for t in texts],
        [re.sub(r"[^\w\s]", " ", (t or "")).lower() or "empty document" for t in texts],
        [f"candidate document {i} {(t or '')}" for i, t in enumerate(texts)],
    ]

    for prepared in attempts:
        try:
            matrix = vectorizer.fit_transform(prepared)
            return cosine_similarity(matrix).tolist()
        except ValueError:
            continue

    return None


def detect_duplicates(candidates: list[ParsedResume]) -> list[tuple[str, str, float]]:
    """
    Detect potentially duplicate resumes among candidates.

    Args:
        candidates: List of parsed and scored candidates.

    Returns:
        List of tuples (filename_a, filename_b, similarity_percentage)
        for pairs exceeding the duplicate threshold. Never raises on bad text input.
    """
    if len(candidates) < 2:
        return []

    try:
        texts = [c.cleaned_text or c.raw_text or "" for c in candidates]
        matrix = _safe_pairwise_matrix(texts)
        if matrix is None:
            return []

        duplicates: list[tuple[str, str, float]] = []
        for i in range(len(candidates)):
            for j in range(i + 1, len(candidates)):
                similarity = round(matrix[i][j] * 100, 1)
                if similarity >= DUPLICATE_SIMILARITY_THRESHOLD * 100:
                    duplicates.append((
                        candidates[i].filename,
                        candidates[j].filename,
                        similarity,
                    ))
        return duplicates
    except Exception:
        return []
