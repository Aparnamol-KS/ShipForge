import subprocess
from pathlib import Path


def clone_repository(
    repository_url: str,
    destination: Path,
) -> None:
    # --depth 1 : download the latest commit instead of the entire Git history
    result = subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            repository_url,
            str(destination),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        output = result.stdout + result.stderr

        raise RuntimeError(f"Failed to clone repository:\n{output}")
