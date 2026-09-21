from app.database.models import (
    Build,
    BuildStatus,
    Project,
)
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timezone


from app.builds.exceptions import InvalidBuildTransitionError



def create_build(
    db: Session,
    project_id: int,
    branch: str | None = None,
    commit_sha: str | None = None,
):
    statement = select(Project).where(Project.id == project_id).with_for_update()

    result = db.execute(statement)
    project = result.scalar_one_or_none()

    if project is None:
        return None

    latest_build_statement = (
        select(Build.build_number)
        .where(Build.project_id == project_id)
        .order_by(Build.build_number.desc())
        .limit(1)
    )

    latest_build_number = db.execute(latest_build_statement).scalar_one_or_none()

    next_build_number = 1 if latest_build_number is None else latest_build_number + 1

    build = Build(
        project_id=project_id,
        build_number=next_build_number,
        branch=branch,
        commit_sha=commit_sha,
        status=BuildStatus.QUEUED,
    )

    db.add(build)
    db.commit()
    db.refresh(build)

    return build


def get_builds(
    db: Session,
    project_id: int,
) -> list[Build]:
    statement = (
        select(Build).where(Build.project_id == project_id).order_by(Build.id.desc())
    )

    result = db.execute(statement)

    return list(result.scalars().all())


def get_build(
    db: Session,
    project_id: int,
    build_id: int,
) -> Build | None:
    statement = select(Build).where(
        Build.id == build_id,
        Build.project_id == project_id,
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()


def transition_build(
    db: Session,
    project_id: int,
    build_id: int,
    new_status: BuildStatus,
) -> Build | None:
    build = get_build(
        db,
        project_id,
        build_id,
    )

    if build is None:
        return None

    current_status = build.status

    allowed_transitions = {
        BuildStatus.QUEUED: {
            BuildStatus.RUNNING,
        },
        BuildStatus.RUNNING: {
            BuildStatus.SUCCESS,
            BuildStatus.FAILED,
        },
        BuildStatus.SUCCESS: set(),
        BuildStatus.FAILED: set(),
    }

    if new_status not in allowed_transitions[current_status]:
        raise InvalidBuildTransitionError(
            f"Cannot transition build from {current_status.value} to {new_status.value}"
        )

    now = datetime.now(timezone.utc)

    build.status = new_status

    if new_status == BuildStatus.RUNNING:
        build.started_at = now

    if new_status in {
        BuildStatus.SUCCESS,
        BuildStatus.FAILED,
    }:
        build.finished_at = now

    db.commit()
    db.refresh(build)

    return build