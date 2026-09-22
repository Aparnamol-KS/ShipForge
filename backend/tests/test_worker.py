import subprocess

from app.builds.service import create_build
from app.database.models import BuildStatus
from app.projects.schemas import ProjectCreate
from app.projects.service import create_project
from app.redis_client.connection import redis_client
from app.redis_client.queue import BUILD_QUEUE, enqueue_build
from app.redis_client.worker import run_worker
from tests.conftest import TestSessionLocal


def test_worker_processes_build(tmp_path, client):
    redis_client.delete(BUILD_QUEUE)

    source_repo = tmp_path / "source"
    source_repo.mkdir()

    subprocess.run(
        ["git", "init"],
        cwd=source_repo,
        check=True,
        capture_output=True,
        text=True,
    )

    hello_file = source_repo / "hello.py"
    hello_file.write_text('print("Hello from worker!")\n')

    subprocess.run(
        ["git", "add", "."],
        cwd=source_repo,
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [
            "git",
            "-c",
            "user.name=ShipForge Test",
            "-c",
            "user.email=test@shipforge.local",
            "commit",
            "-m",
            "Initial commit",
        ],
        cwd=source_repo,
        check=True,
        capture_output=True,
        text=True,
    )

    db = TestSessionLocal()

    try:
        project = create_project(
            db,
            ProjectCreate(
                name="Worker Test",
                description="Worker integration test",
                repository_url=str(source_repo),
                build_command="python hello.py",
            ),
        )

        build = create_build(
            db,
            project.id,
        )

        enqueue_build(
            build_id=build.id,
            project_id=project.id,
        )

    finally:
        db.close()

    run_worker(once=True)

    db = TestSessionLocal()

    try:
        processed_build = db.get(
            type(build),
            build.id,
        )

        assert processed_build is not None
        assert processed_build.status == BuildStatus.SUCCESS

    finally:
        db.close()
