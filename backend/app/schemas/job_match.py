from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobMatchResponse(BaseModel):
    id: int
    job_id: int
    analysis: dict
    profile_version: str
    prompt_version: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    candidate_profile_id: int | None = None