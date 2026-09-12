from pathlib import Path

from app.builds.workspace_service import (
    cleanup_workspace,
    create_workspace,
)


def test_create_workspace():
    workspace = create_workspace()

    try:
        assert workspace.exists()
        assert workspace.is_dir()
    finally:
        cleanup_workspace(workspace)


def test_cleanup_workspace():
    workspace = create_workspace()

    test_file = workspace / "test.txt"
    test_file.write_text("hello")

    assert test_file.exists()

    cleanup_workspace(workspace)

    assert not workspace.exists()
