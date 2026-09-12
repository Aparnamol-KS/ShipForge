from pathlib import Path

from fastapi import BackgroundTasks

from app.builds.runner import run_build


def schedule_build(
    background_tasks: BackgroundTasks,
    project_id: int,
    build_id: int,
    workspace: Path,
    command: str,
) -> None:
    background_tasks.add_task(
        run_build,
        project_id,
        build_id,
        workspace,
        command,
    )
