from app.builds.exceptions import InvalidBuildTransitionError
from app.builds.schemas import (
    BuildResponse,
    BuildStatusUpdate,
)
from app.builds.service import (
    create_build,
    get_build,
    get_builds,
    transition_build,
)
from app.database.connection import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/projects/{project_id}/builds",
    tags=["Builds"],
)


@router.post("/", response_model=BuildResponse, status_code=201)
def create_build_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
):
    build = create_build(db, project_id)

    if build is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
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
