from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.projects.service import get_project_by_repository
from app.builds.service import create_build
from app.database.connection import get_db


router = APIRouter(
    prefix="/webhooks",
    tags=["webhooks"],
)


@router.post("/github")
async def github_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    payload = await request.json()

    repository = payload.get("repository", {})

    repository_url = repository.get("clone_url")
    branch = payload.get("ref")
    commit_sha = payload.get("after")

    if not repository_url:
        return {
            "message": "Repository URL missing",
        }

    project = get_project_by_repository(
        db,
        repository_url,
    )

    if project is None:
        return {
            "message": "No ShipForge project found",
            "repository_url": repository_url,
        }

    build = create_build(
        db,
        project.id,
    )

    return {
        "message": "Build queued",
        "project_id": project.id,
        "project_name": project.name,
        "build_id": build.id,
        "build_number": build.build_number,
        "status": build.status,
        "repository_url": repository_url,
        "branch": branch,
        "commit_sha": commit_sha,
    }
