from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    company: Mapped[str] = mapped_column(String(255))
    job_title: Mapped[str] = mapped_column(String(255))

    job_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)

    application_date: Mapped[date] = mapped_column(Date)

    status: Mapped[str] = mapped_column(
        String(50),
        default="Applied"
    )

    resume_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    job_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )