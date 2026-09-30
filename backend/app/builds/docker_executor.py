import subprocess
from pathlib import Path
from collections.abc import Callable

BUILD_WORKSPACE_VOLUME = "shipforge_build_workspaces"
BUILD_NETWORK = "shipforge_default"

def run_command(
    command: str,
    workspace: Path | None = None,
    build_id: int | None = None,
    is_cancelled: Callable[[], bool] | None = None,
) -> tuple[int, str]:

    docker_command = [
        "docker",
        "run",
        "--rm",
        "--volume",
        "/var/run/docker.sock:/var/run/docker.sock",
        "--network",
        BUILD_NETWORK,
        "-e",
        "DATABASE_URL=postgresql+psycopg2://shipforge:shipforge_password@postgres:5432/shipforge",
        "-e",
        "TEST_DATABASE_URL=postgresql+psycopg2://shipforge:shipforge_password@postgres:5432/shipforge_test",
        "-e",
        "REDIS_URL=redis://redis:6379/0",
    ]

    if build_id is not None:
        docker_command.extend(
            [
                "--name",
                f"shipforge-build-{build_id}",
            ]
        )

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

    process = subprocess.Popen(
            docker_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )


    while process.poll() is None:
        if is_cancelled is not None and is_cancelled():
            if build_id is not None:
                stop_build_container(build_id)

            process.wait()
            break

        try:
            process.wait(timeout=0.5)
        except subprocess.TimeoutExpired:
            continue

    stdout, stderr = process.communicate()
    output = stdout + stderr

    return process.returncode, output


def stop_build_container(build_id: int) -> None:
    container_name = f"shipforge-build-{build_id}"

    subprocess.run(
        [
            "docker",
            "stop",
            container_name,
        ],
        capture_output=True,
        text=True,
        check=False,
    )