"""Document text extraction for PDF and DOCX resume uploads."""

import re
from io import BytesIO
from typing import BinaryIO, Union

from docx import Document
from pypdf import PdfReader


def extract_text_from_pdf(uploaded_file: Union[BinaryIO, BytesIO]) -> str:
    """
    Extract raw text from all pages of an uploaded PDF file.

    Args:
        uploaded_file: A file-like object from Streamlit or FastAPI upload.

    Returns:
        Concatenated text from all PDF pages, or an empty string on failure.
    """
    try:
        uploaded_file.seek(0)
        reader = PdfReader(uploaded_file)
        pages_text: list[str] = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages_text.append(page_text)

        return "\n".join(pages_text).strip()
    except Exception:
        return ""


def extract_text_from_docx(uploaded_file: Union[BinaryIO, BytesIO]) -> str:
    """
    Extract raw text from an uploaded DOCX file.

    Args:
        uploaded_file: A file-like object from Streamlit or FastAPI upload.

    Returns:
        Concatenated paragraph text, or an empty string on failure.
    """
    try:
        uploaded_file.seek(0)
        document = Document(uploaded_file)
        paragraphs = [para.text.strip() for para in document.paragraphs if para.text.strip()]
        return "\n".join(paragraphs).strip()
    except Exception:
        return ""


def extract_text_from_document(uploaded_file: Union[BinaryIO, BytesIO], filename: str) -> str:
    """
    Route document extraction based on file extension.

    Args:
        uploaded_file: Uploaded file object.
        filename: Original filename including extension.

    Returns:
        Extracted raw text from the document.
    """
    extension = filename.rsplit(".", 1)[-1].lower()
    if extension == "pdf":
        return extract_text_from_pdf(uploaded_file)
    if extension in ("docx", "doc"):
        return extract_text_from_docx(uploaded_file)
    return ""


def extract_candidate_name_from_filename(filename: str) -> str:
    """
    Derive a candidate name from an uploaded filename.

    Args:
        filename: Original uploaded filename (e.g., ``suraj_resume_v2.pdf``).

    Returns:
        Title-cased candidate name (e.g., ``Suraj``).
    """
    base_name = filename.rsplit(".", 1)[0]
    tokens = re.split(r"[_\-\s]+", base_name.lower())

    skip_words = {"resume", "cv", "curriculum", "vitae", "final", "draft", "copy", "new", "updated"}
    for token in tokens:
        cleaned = re.sub(r"[^a-z]", "", token)
        if not cleaned or cleaned in skip_words or cleaned.isdigit():
            continue
        if re.fullmatch(r"v\d+", cleaned):
            continue
        return cleaned.capitalize()

    return base_name.replace("_", " ").replace("-", " ").title()
