import os
import shutil
import stat
import tempfile
from pathlib import Path


def create_workspace() -> Path:
    workspace_root = Path("/build_workspaces")
    workspace_root.mkdir(parents=True, exist_ok=True)

    workspace = Path(
        tempfile.mkdtemp(
            prefix="shipforge-build-",
            dir=workspace_root,
        )
    )

    return workspace

def _remove_readonly(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def cleanup_workspace(workspace: Path) -> None:
    if workspace.exists():
        shutil.rmtree(
            workspace,
            onexc=_remove_readonly,
        )
