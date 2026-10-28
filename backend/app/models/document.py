
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    filename: Mapped[str] = mapped_column(String(255))
    document_type: Mapped[str] = mapped_column(String(50))

    # Relative path to the original uploaded file
    file_path: Mapped[str] = mapped_column(String(1000))

    # Extracted text used by future AI agents and RAG
    extracted_text: Mapped[str] = mapped_column(Text)

    application_id: Mapped[int | None] = mapped_column(
        ForeignKey("applications.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )