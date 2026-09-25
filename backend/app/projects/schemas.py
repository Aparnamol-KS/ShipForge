from datetime import datetime

from pydantic import BaseModel, ConfigDict

# represents what the client is allowed to send
class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    repository_url: str | None = None
    install_command: str | None = None
    test_command: str | None = None
    build_command: str | None = None

# represents what our API sends back
class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    repository_url: str | None
    install_command: str | None
    test_command: str | None
    build_command: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# represents modifying an existing project.
class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    repository_url: str | None = None
    install_command: str | None = None
    test_command: str | None = None
    build_command: str | None = None