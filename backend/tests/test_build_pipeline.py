import subprocess

from app.builds.runner import run_build
from app.database.models import BuildStatus
from tests.conftest import TestSessionLocal


def test_real_build_pipeline(client, tmp_path):
    # Create a local Git repository
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
    hello_file.write_text(
        'print("Hello from ShipForge!")\nprint("Real pipeline works!")\n'
    )

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

    # Create a ShipForge project
    response = client.post(
        "/projects/",
        json={
            "name": "Pipeline Test",
            "repository_url": str(source_repo),
            "build_command": "python hello.py",
        },
    )

    assert response.status_code == 201

    project_id = response.json()["id"]

    # Create the build
    response = client.post(
        f"/projects/{project_id}/builds/",
    )

    assert response.status_code == 201

    build_id = response.json()["id"]

    # Run the actual pipeline
    run_build(
        project_id,
        build_id,
        repository_url=str(source_repo),
        command="python hello.py",
        session_factory=TestSessionLocal,
    )

    # Verify build status
    response = client.get(
        f"/projects/{project_id}/builds/{build_id}",
    )

    assert response.status_code == 200

    build = response.json()

    assert build["status"] == BuildStatus.SUCCESS.value

    # Verify logs
    response = client.get(
        f"/projects/{project_id}/builds/{build_id}/logs",
    )

    assert response.status_code == 200

    logs = response.json()

    assert len(logs) == 1

    assert "Hello from ShipForge!" in logs[0]["output"]
    assert "Real pipeline works!" in logs[0]["output"]
