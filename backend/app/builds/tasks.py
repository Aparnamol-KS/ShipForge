from app.builds.runner import run_build
from fastapi import BackgroundTasks


def schedule_build(
    background_tasks: BackgroundTasks,
    project_id: int,
    build_id: int,
    repository_url: str,
    command: str,
) -> None:

    background_tasks.add_task(
        run_build,
        project_id,
        build_id,
        repository_url,
        command,
    )
