from app.database.models import Build, BuildStatus
from app.projects.service import get_project
from sqlalchemy import select
from sqlalchemy.orm import Session


def create_build(
    db: Session,
    project_id: int,
) -> Build | None:
    project = get_project(db, project_id)

    if project is None:
        return None

    build = Build(
        project_id=project_id,
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
