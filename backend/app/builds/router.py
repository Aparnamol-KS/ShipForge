from app.builds.exceptions import InvalidBuildTransitionError
from app.builds.schemas import BuildResponse, BuildStatusUpdate, BuildLogResponse
from app.builds.service import (
    create_build,
    get_build,
    get_builds,
    transition_build,
)
from app.database.connection import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.builds.tasks import schedule_build
from app.builds.log_service import get_build_logs
from app.projects.service import get_project
from fastapi import WebSocket
from app.builds.websocket import manager
from app.builds.event_listener import forward_build_events
import asyncio

router = APIRouter(
    prefix="/projects/{project_id}/builds",
    tags=["Builds"],
)


@router.post(
    "/",
    response_model=BuildResponse,
    status_code=201,
)
def create_build_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = get_project(
        db,
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    if not project.repository_url:
        raise HTTPException(
            status_code=400,
            detail="Project repository URL is required",
        )

    if not project.build_command:
        raise HTTPException(
            status_code=400,
            detail="Project build command is required",
        )

    build = create_build(
        db,
        project_id,
    )

    if build is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    schedule_build(
        project_id=project_id,
        build_id=build.id,
    )

    return build



@router.get(
    "/",
    response_model=list[BuildResponse],
)
def get_builds_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
):
    return get_builds(db, project_id)


@router.get(
    "/{build_id}",
    response_model=BuildResponse,
)
def get_build_endpoint(
    project_id: int,
    build_id: int,
    db: Session = Depends(get_db),
):
    build = get_build(db, project_id, build_id)

    if build is None:
        raise HTTPException(
            status_code=404,
            detail="Build not found",
        )

    return build


@router.patch(
    "/{build_id}",
    response_model=BuildResponse,
)
def transition_build_endpoint(
    project_id: int,
    build_id: int,
    status_data: BuildStatusUpdate,
    db: Session = Depends(get_db),
):
    try:
        build = transition_build(
            db,
            project_id,
            build_id,
            status_data.status,
        )
    except InvalidBuildTransitionError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    if build is None:
        raise HTTPException(
            status_code=404,
            detail="Build not found",
        )

    return build


@router.get(
    "/{build_id}/logs",
    response_model=list[BuildLogResponse],
)
def get_logs(
    project_id: int,
    build_id: int,
    db: Session = Depends(get_db),
):
    build = get_build(
        db,
        project_id,
        build_id,
    )

    if build is None:
        raise HTTPException(
            status_code=404,
            detail="Build not found",
        )

    return get_build_logs(
        db,
        build_id,
    )

@router.websocket("/{build_id}/ws")
async def build_websocket(
    websocket: WebSocket,
    build_id: int,
):
    await manager.connect(build_id, websocket)

    try:
        await forward_build_events(
            build_id,
            websocket,
        )
    except Exception:
        manager.disconnect(
            build_id,
            websocket,
        )