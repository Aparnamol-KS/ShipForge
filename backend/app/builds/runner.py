import time

from sqlalchemy.orm import Session

from app.builds.service import transition_build
from app.database.connection import SessionLocal
from app.database.models import BuildStatus


def run_build(
    project_id: int,
    build_id: int,
    sleep_fn=time.sleep,
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

        sleep_fn(5)

        transition_build(
            db,
            project_id,
            build_id,
            BuildStatus.SUCCESS,
        )

    finally:
        db.close()
