import subprocess
from pathlib import Path


BUILD_WORKSPACE_VOLUME = "shipforge_build_workspaces"


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
        workspace_name = workspace.name

        docker_command.extend(
            [
                "-v",
                f"{BUILD_WORKSPACE_VOLUME}:/workspace",
                "-w",
                f"/workspace/{workspace_name}",
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
