from sqlalchemy.orm import Session

from app.database.models import Project
from app.projects.schemas import ProjectCreate

from sqlalchemy import select



def create_project(db: Session, project_data: ProjectCreate) -> Project:
    project = Project(
        name=project_data.name,
        description=project_data.description,
        repository_url=project_data.repository_url,
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