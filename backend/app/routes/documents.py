
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

from app.models.candidate_profile import CandidateProfile
from app.schemas.candidate_profile import CandidateProfileResponse
from sqlalchemy.exc import SQLAlchemyError

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
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    if document.document_type != "cv":
        raise HTTPException(
            status_code=400,
            detail="Only CV documents can be analysed",
        )

    if not document.extracted_text:
        raise HTTPException(
            status_code=400,
            detail="No extracted text available for this document",
        )

    # Step 1: Analyse the CV
    try:
        analysis = analyse_profile(document.extracted_text)

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Profile analysis failed",
        )

    # Step 2: Save the analysis
    profile = CandidateProfile(
        document_id=document.id,
        analysis=analysis,
        profile_version="profile-v1",
        prompt_version="profile-analyst-v1",
    )

    try:
        db.add(profile)
        db.commit()
        db.refresh(profile)

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Could not save candidate profile",
        )

    # Step 3: Return the saved profile
    return {
        "id": profile.id,
        "document_id": profile.document_id,
        "filename": document.filename,
        "profile_version": profile.profile_version,
        "prompt_version": profile.prompt_version,
        "analysis": profile.analysis,
        "created_at": profile.created_at,
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

@router.get(
    "/{document_id}/profiles",
    response_model=list[CandidateProfileResponse],
)
def get_document_profiles(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    profiles = (
        db.query(CandidateProfile)
        .filter(CandidateProfile.document_id == document_id)
        .order_by(
            CandidateProfile.created_at.desc(),
            CandidateProfile.id.desc(),
        )
        .all()
    )

    return profiles