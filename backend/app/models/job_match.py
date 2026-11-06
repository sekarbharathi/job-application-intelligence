from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base

from sqlalchemy import ForeignKey, Integer

class JobMatch(Base):
    __tablename__ = "job_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        nullable=False,
        index=True,
    )

    # Complete AI matching result
    analysis: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Records which profile and prompt generated this result
    profile_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    prompt_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    candidate_profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("candidate_profiles.id"),
        nullable=True,
        index=True,
    )