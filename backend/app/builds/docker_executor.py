import subprocess
from pathlib import Path


def run_command(
    command: str,
    workspace: Path | None = None,
) -> tuple[int, str]:

    docker_command = [
        "docker",
        "run",
        "--rm",
    ]

    if workspace is not None:
        docker_command.extend(
            [
                "-v",
                f"{workspace.resolve()}:/workspace",
                "-w",
                "/workspace",
            ]
        )

    docker_command.extend(
        [
            "python:3.12-slim",
            "sh",
            "-c",
            command,
        ]
    )

    result = subprocess.run(
        docker_command,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr

    return result.returncode, output
