import subprocess

from app.builds.workspace_service import (
    cleanup_workspace,
    create_workspace,
)
from app.repositories.service import clone_repository


def test_clone_repository_into_workspace(tmp_path):
    source_repo = tmp_path / "source"

    source_repo.mkdir()

    subprocess.run(
        ["git", "init"],
        cwd=source_repo,
        check=True,
        capture_output=True,
        text=True,
    )

    test_file = source_repo / "hello.py"
    test_file.write_text('print("Hello from repository!")\n')

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

    workspace = create_workspace()

    try:
        clone_repository(
            str(source_repo),
            workspace,
        )

        cloned_file = workspace / "hello.py"

        assert cloned_file.exists()
        assert cloned_file.read_text() == 'print("Hello from repository!")\n'

    finally:
        cleanup_workspace(workspace)
