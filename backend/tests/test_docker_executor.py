from app.builds.docker_executor import run_command
from pathlib import Path
import subprocess



def test_run_command_success():
    exit_code, output = run_command("python --version")

    assert exit_code == 0
    assert "Python" in output


def test_run_command_failure():
    exit_code, output = run_command("python -c \"raise Exception('build failed')\"")

    assert exit_code != 0
    assert "build failed" in output

def test_run_command_with_workspace(tmp_path: Path):
    workspace_name = tmp_path.name

    create_file_command = [
        "docker",
        "run",
        "--rm",
        "-v",
        "shipforge_build_workspaces:/workspace",
        "python:3.12-slim",
        "sh",
        "-c",
        (
            f"mkdir -p /workspace/{workspace_name} && "
            f"printf \"print('Hello from ShipForge')\\n\" "
            f"> /workspace/{workspace_name}/hello.py"
        ),
    ]

    subprocess.run(
        create_file_command,
        check=True,
    )

    exit_code, output = run_command(
        "python hello.py",
        workspace=tmp_path,
    )

    assert exit_code == 0
    assert "Hello from ShipForge" in output