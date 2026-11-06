from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CandidateProfileResponse(BaseModel):
    id: int
    document_id: int
    analysis: dict
    profile_version: str
    prompt_version: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)