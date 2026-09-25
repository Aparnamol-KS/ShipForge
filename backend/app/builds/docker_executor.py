import subprocess
from pathlib import Path


BUILD_WORKSPACE_VOLUME = "shipforge_build_workspaces"
BUILD_NETWORK = "shipforge_default"

def run_command(
    command: str,
    workspace: Path | None = None,
) -> tuple[int, str]:

    docker_command = [
        "docker",
        "run",
        "--rm",
        "--network",
        BUILD_NETWORK,
        "-e",
        "DATABASE_URL=postgresql+psycopg2://shipforge:shipforge_password@postgres:5432/shipforge",
        "-e",
        "TEST_DATABASE_URL=postgresql+psycopg2://shipforge:shipforge_password@postgres:5432/shipforge_test",
        "-e",
        "REDIS_URL=redis://redis:6379/0",
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
            "shipforge-build:latest",
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
