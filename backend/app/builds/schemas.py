from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.database.models import BuildStatus


class BuildCreate(BaseModel):
    pass


class BuildResponse(BaseModel):
    id: int
    project_id: int
    status: BuildStatus
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
