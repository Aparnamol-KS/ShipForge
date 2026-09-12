import time

from sqlalchemy.orm import Session

from app.builds.service import transition_build
from app.database.connection import SessionLocal
from app.database.models import BuildStatus
from pathlib import Path

from app.builds.docker_executor import run_command


def run_build(
    project_id: int,
    build_id: int,
    workspace: Path,
    command: str,
    session_factory=SessionLocal,
) -> None:
    db: Session = session_factory()

    try:
        transition_build(
            db,
            project_id,
            build_id,
            BuildStatus.RUNNING,
        )

        exit_code, output = run_command(
            command,
            workspace=workspace,
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
        db.close()