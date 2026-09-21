from fastapi import APIRouter, Depends, Request, BackgroundTasks,HTTPException
from sqlalchemy.orm import Session
import os
from app.projects.service import get_project_by_repository
from app.builds.service import create_build
from app.database.connection import get_db
from app.builds.tasks import schedule_build
from app.webhooks.security import verify_github_signature


router = APIRouter(
    prefix="/webhooks",
    tags=["webhooks"],
)


@router.post("/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    payload = await request.body()

    signature = request.headers.get(
        "X-Hub-Signature-256"
    )

    secret = os.getenv(
        "GITHUB_WEBHOOK_SECRET"
    )

    if not secret:
        raise HTTPException(
            status_code=500,
            detail="GitHub webhook secret is not configured",
        )

    if not verify_github_signature(
        payload,
        signature,
        secret,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid GitHub webhook signature",
        )

    data = await request.json()

    repository = data.get("repository", {})

    repository_url = repository.get("clone_url")
    branch = data.get("ref")
    commit_sha = data.get("after")

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

    if not project.build_command:
        return {
            "message": "Project build command is required",
            "project_id": project.id,
        }

    schedule_build(
        background_tasks,
        project.id,
        build.id,
        repository_url=project.repository_url,
        command=project.build_command,
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
