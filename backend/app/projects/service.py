from app.database.models import Project
from app.projects.schemas import ProjectCreate, ProjectUpdate
from sqlalchemy import select
from sqlalchemy.orm import Session


def create_project(db: Session, project_data: ProjectCreate) -> Project:
    project = Project(
        name=project_data.name,
        description=project_data.description,
        repository_url=project_data.repository_url,
        build_command=project_data.build_command,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def get_projects(db: Session) -> list[Project]:
    statement = select(Project).order_by(Project.id)

    result = db.execute(statement)
    # extracts the actual Project objects from the SQLAlchemy result
    return list(result.scalars().all())


def get_project(db: Session, project_id: int) -> Project | None:
    statement = select(Project).where(Project.id == project_id)

    result = db.execute(statement)

    return result.scalar_one_or_none()

def get_project_by_repository(
    db: Session,
    repository_url: str,
) -> Project | None:
    statement = select(Project).where(Project.repository_url == repository_url)

    result = db.execute(statement)

    return result.scalar_one_or_none()


def update_project(
    db: Session,
    project_id: int,
    project_data: ProjectUpdate,
) -> Project | None:
    project = get_project(db, project_id)

    if project is None:
        return None

    update_data = project_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)

    return project


def delete_project(db: Session, project_id: int) -> bool:
    project = get_project(db, project_id)

    if project is None:
        return False

    db.delete(project)
    db.commit()

    return True
