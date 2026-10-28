
from io import BytesIO

from docx import Document
from fastapi import HTTPException
from pypdf import PdfReader

import re


ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def extract_text(filename: str, content: bytes) -> str:
    """Extract text from a PDF or DOCX file."""

    filename_lower = filename.lower()

    try:
        if filename_lower.endswith(".pdf"):
            reader = PdfReader(BytesIO(content))
            text = "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )

        elif filename_lower.endswith(".docx"):
            document = Document(BytesIO(content))
            text = "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
            )

        else:
            raise HTTPException(
                status_code=400,
                detail="Only PDF and DOCX files are supported.",
            )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Could not read the document. Check that the file is valid.",
        ) from exc

    # Fix words split across PDF line breaks, e.g. "build-\ning".
    text = re.sub(r"-\s*\n\s*", "", text)

    # Normalize line endings and remove unnecessary whitespace.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="No readable text found. Scanned PDFs may require OCR.",
        )

    return text