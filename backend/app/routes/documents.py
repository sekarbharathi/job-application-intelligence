
import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from app.services.profile_analyst import analyse_profile
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.document import Document
from app.models.application import Application
from app.services.document_service import extract_text

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

MAX_FILE_SIZE = 5 * 1024 * 1024

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_document(
    document_type: str = Form(...),
    application_id: int | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()

    if suffix not in {".pdf", ".docx"}:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported.",
        )

    if document_type not in {"cv", "cover_letter"}:
        raise HTTPException(
            status_code=400,
            detail="document_type must be 'cv' or 'cover_letter'.",
        )

    if application_id is not None:
        application = db.get(Application, application_id)
        if application is None:
            raise HTTPException(
                status_code=404,
                detail="Application not found.",
            )

    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File is too large. Maximum size is 5 MB.",
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    text = extract_text(filename, content)

    stored_filename = f"{uuid4().hex}{suffix}"
    destination = UPLOAD_DIR / stored_filename

    try:
        destination.write_bytes(content)

        document = Document(
            filename=Path(filename).name,
            document_type=document_type,
            file_path=str(destination.relative_to(UPLOAD_DIR.parent)),
            extracted_text=text,
            application_id=application_id,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

    except Exception:
        db.rollback()
        destination.unlink(missing_ok=True)
        raise

    return {
        "id": document.id,
        "filename": document.filename,
        "document_type": document.document_type,
        "application_id": document.application_id,
        "character_count": len(document.extracted_text),
        "message": "Document uploaded and saved successfully.",
    }


@router.get("/")
def list_documents(db: Session = Depends(get_db)):
    documents = (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .all()
    )

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "document_type": document.document_type,
            "application_id": document.application_id,
            "character_count": len(document.extracted_text),
            "created_at": document.created_at,
        }
        for document in documents
    ]

@router.post("/{document_id}/analyse-profile")
def analyse_saved_profile(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    if document.document_type != "cv":
        raise HTTPException(
            status_code=400,
            detail="Profile analysis requires a CV document.",
        )

    try:
        analysis = analyse_profile(document.extracted_text)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Profile analysis failed. Check the AI configuration and try again.",
        ) from exc

    return {
        "document_id": document.id,
        "filename": document.filename,
        "analysis": analysis,
    }


@router.get("/{document_id}/text")
def get_document_text(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return {
        "document_id": document.id,
        "filename": document.filename,
        "extracted_text": document.extracted_text,
    }


@router.post("/{document_id}/re-extract")
def re_extract_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    file_path = UPLOAD_DIR.parent / document.file_path
    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Original uploaded file not found.",
        )

    text = extract_text(
        document.filename,
        file_path.read_bytes(),
    )

    document.extracted_text = text
    db.commit()
    db.refresh(document)

    return {
        "document_id": document.id,
        "filename": document.filename,
        "character_count": len(text),
        "message": "Document text re-extracted successfully.",
    }