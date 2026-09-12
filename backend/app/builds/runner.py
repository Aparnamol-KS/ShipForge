from pathlib import Path

from sqlalchemy.orm import Session

from app.builds.docker_executor import run_command
from app.builds.log_service import create_build_log
from app.builds.service import transition_build
from app.builds.workspace_service import (
    cleanup_workspace,
    create_workspace,
)
from app.database.connection import SessionLocal
from app.database.models import BuildStatus
from app.repositories.service import clone_repository

def run_build(
    project_id: int,
    build_id: int,
    repository_url: str,
    command: str,
    session_factory=SessionLocal,
    workspace_factory=create_workspace,
    repository_cloner=clone_repository,
    command_runner=run_command,
    workspace_cleaner=cleanup_workspace,
) -> None:
    db: Session = session_factory()
    workspace: Path | None = None

    try:
        transition_build(
            db,
            project_id,
            build_id,
            BuildStatus.RUNNING,
        )

        workspace = workspace_factory()

        repository_cloner(
            repository_url,
            workspace,
        )

        exit_code, output = command_runner(
            command,
            workspace=workspace,
        )

        create_build_log(
            db,
            build_id,
            output,
        )

        if exit_code == 0:
            transition_build(
                db,
                project_id,
                build_id,
                BuildStatus.SUCCESS,
            )
        else:
            transition_build(
                db,
                project_id,
                build_id,
                BuildStatus.FAILED,
            )

    finally:
        if workspace is not None:
            workspace_cleaner(workspace)

        db.close()
