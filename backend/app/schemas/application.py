from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ApplicationCreate(BaseModel):
    company: str
    job_title: str

    job_url: str | None = None
    location: str | None = None
    source: str | None = None

    application_date: date
    status: str = "Applied"

    resume_version: str | None = None
    job_description: str | None = None
    notes: str | None = None


class ApplicationResponse(ApplicationCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)