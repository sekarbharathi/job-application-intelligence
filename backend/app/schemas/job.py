from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobCreate(BaseModel):
    company: str
    job_title: str

    job_url: str | None = None
    location: str | None = None
    source: str | None = None

    job_description: str


class JobUpdate(BaseModel):
    company: str | None = None
    job_title: str | None = None
    job_url: str | None = None
    location: str | None = None
    source: str | None = None
    job_description: str | None = None
    status: str | None = None


class JobResponse(JobCreate):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)