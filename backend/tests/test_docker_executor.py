from app.builds.docker_executor import run_command
from pathlib import Path



def test_run_command_success():
    exit_code, output = run_command("python --version")

    assert exit_code == 0
    assert "Python" in output


def test_run_command_failure():
    exit_code, output = run_command("python -c \"raise Exception('build failed')\"")

    assert exit_code != 0
    assert "build failed" in output

def test_run_command_with_workspace(tmp_path: Path):
    hello_file = tmp_path / "hello.py"

    hello_file.write_text("print('Hello from ShipForge')")

    exit_code, output = run_command(
        "python hello.py",
        workspace=tmp_path,
    )

    assert exit_code == 0
    assert "Hello from ShipForge" in output