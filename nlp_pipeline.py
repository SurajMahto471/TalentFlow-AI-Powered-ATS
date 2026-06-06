"""Text preprocessing, vectorization, and similarity scoring for resume screening."""

import re
from typing import List

import spacy
from typing import Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def _load_spacy_model(name: str = "en_core_web_sm") -> spacy.language.Language:
    """Robustly load a spaCy model.

    Strategy:
    1. Try `spacy.load(name)`.
    2. Try importing the model package (en_core_web_sm) and calling `.load()`.
    3. Try `spacy.cli.download(name)` then `spacy.load(name)`.
    4. Fall back to `spacy.blank('en')`.
    """
    import importlib
    import sys

    try:
        return spacy.load(name)
    except Exception as e1:  # pragma: no cover - runtime environments differ
        print(f"spacy.load('{name}') failed: {e1}")

    # Try to import the model module directly (installed via pip as en-core-web-sm)
    try:
        mod_name = name.replace("-", "_")
        model_mod = importlib.import_module(mod_name)
        try:
            return model_mod.load()
        except Exception as e_mod_load:
            print(f"{mod_name}.load() failed: {e_mod_load}")
    except Exception as e2:
        print(f"import of model package failed: {e2}")

    # Try to use spaCy's download helper
    try:
        from spacy.cli import download as _spacy_download

        _spacy_download(name)
        return spacy.load(name)
    except Exception as e3:
        print(f"spaCy download/load attempt failed: {e3}")

    # Final fallback: blank English model
    print("Falling back to spaCy blank('en') model. Some NER/lemmatization may be limited.")
    return spacy.blank("en")


_nlp = _load_spacy_model()


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

    doc = _nlp(cleaned)
    tokens = [
        token.text
        for token in doc
        if not token.is_stop and not token.is_space and token.text.strip()
    ]

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
