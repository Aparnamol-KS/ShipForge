from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.database.models import BuildStatus


class BuildCreate(BaseModel):
    pass


class BuildResponse(BaseModel):
    id: int
    project_id: int
    build_number: int
    branch: str | None
    commit_sha: str | None
    status: BuildStatus
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

class BuildStatusUpdate(BaseModel):
    status: BuildStatus

class BuildLogResponse(BaseModel):
    id: int
    build_id: int
    output: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)