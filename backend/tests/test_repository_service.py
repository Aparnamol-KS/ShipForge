import subprocess
from pathlib import Path

from app.repositories.service import clone_repository


def test_clone_repository(tmp_path: Path):
    source = tmp_path / "source"
    destination = tmp_path / "destination"

    source.mkdir()

    subprocess.run(
        ["git", "init"],
        cwd=source,
        check=True,
        capture_output=True,
    )

    hello_file = source / "hello.py"

    hello_file.write_text("print('Hello from repository')")

    subprocess.run(
        ["git", "add", "."],
        cwd=source,
        check=True,
        capture_output=True,
    )

    subprocess.run(
        [
            "git",
            "-c",
            "user.name=ShipForge",
            "-c",
            "user.email=shipforge@example.com",
            "commit",
            "-m",
            "Initial commit",
        ],
        cwd=source,
        check=True,
        capture_output=True,
    )

    clone_repository(
        str(source),
        destination,
    )

    assert destination.exists()
    assert (destination / "hello.py").exists()

    assert (destination / "hello.py").read_text() == "print('Hello from repository')"
