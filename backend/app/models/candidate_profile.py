from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    analysis: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    profile_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="profile-v1",
    )

    prompt_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="profile-analyst-v1",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )