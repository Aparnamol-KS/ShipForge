from app.database.models import (
    Build,
    BuildStatus,
    Project,
)
from sqlalchemy import select
from sqlalchemy.orm import Session


def create_build(
    db: Session,
    project_id: int,
) -> Build | None:
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
