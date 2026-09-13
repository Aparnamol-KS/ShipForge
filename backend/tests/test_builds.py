from app.builds.log_service import create_build_log
from app.builds.runner import run_build
from app.database.models import BuildLog
from app.database.test_database import TestSessionLocal
from fastapi.testclient import TestClient
from sqlalchemy import select


def create_test_project(client: TestClient):
    response = client.post(
        "/projects/",
        json={
            "name": "Test Project",
            "repository_url": "https://example.com/test.git",
            "build_command": "pytest",
        },
    )

    return response.json()["id"]

def test_create_build(client: TestClient):
    project_id = create_test_project(client)

    response = client.post(
        f"/projects/{project_id}/builds/",
    )

    assert response.status_code == 201

    data = response.json()

    assert data["project_id"] == project_id
    assert data["build_number"] == 1
    assert data["status"] == "queued"
    assert data["started_at"] is None
    assert data["finished_at"] is None


def test_create_build_without_repository_url(client: TestClient):
    response = client.post(
        "/projects/",
        json={
            "name": "Test Project",
            "build_command": "pytest",
        },
    )

    project_id = response.json()["id"]

    response = client.post(
        f"/projects/{project_id}/builds/",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == ("Project repository URL is required")


def test_create_build_without_build_command(client: TestClient):
    response = client.post(
        "/projects/",
        json={
            "name": "Test Project",
            "repository_url": "https://example.com/test.git",
        },
    )

    project_id = response.json()["id"]

    response = client.post(
        f"/projects/{project_id}/builds/",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == ("Project build command is required")

def test_get_builds(client: TestClient):
    project_id = create_test_project(client)

    first_response = client.post(
        f"/projects/{project_id}/builds/",
    )

    second_response = client.post(
        f"/projects/{project_id}/builds/",
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    response = client.get(
        f"/projects/{project_id}/builds/",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["project_id"] == project_id
    assert data[0]["build_number"] == 2

    assert data[1]["project_id"] == project_id
    assert data[1]["build_number"] == 1


def test_get_build(client: TestClient):
    project_id = create_test_project(client)

    create_response = client.post(
        f"/projects/{project_id}/builds/",
    )

    build_id = create_response.json()["id"]

    response = client.get(
        f"/projects/{project_id}/builds/{build_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == build_id
    assert data["project_id"] == project_id
    assert data["status"] == "queued"


def test_get_nonexistent_build(client: TestClient):
    project_id = create_test_project(client)

    response = client.get(
        f"/projects/{project_id}/builds/9999",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Build not found"


def test_get_build_from_wrong_project(client: TestClient):
    first_project_id = create_test_project(client)
    second_project_id = create_test_project(client)

    create_response = client.post(
        f"/projects/{first_project_id}/builds/",
    )

    build_id = create_response.json()["id"]

    response = client.get(
        f"/projects/{second_project_id}/builds/{build_id}",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Build not found"


def test_build_numbers_are_project_specific(client: TestClient):
    first_project_id = create_test_project(client)
    second_project_id = create_test_project(client)

    first_build = client.post(
        f"/projects/{first_project_id}/builds/",
    )

    second_build = client.post(
        f"/projects/{first_project_id}/builds/",
    )

    third_build = client.post(
        f"/projects/{second_project_id}/builds/",
    )

    assert first_build.json()["build_number"] == 1
    assert second_build.json()["build_number"] == 2
    assert third_build.json()["build_number"] == 1


def test_transition_build_to_running(client: TestClient):
    project_id = create_test_project(client)

    create_response = client.post(
        f"/projects/{project_id}/builds/",
    )

    build_id = create_response.json()["id"]

    response = client.patch(
        f"/projects/{project_id}/builds/{build_id}",
        json={
            "status": "running",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "running"
    assert data["started_at"] is not None
    assert data["finished_at"] is None


def test_transition_build_to_success(client: TestClient):
    project_id = create_test_project(client)

    create_response = client.post(
        f"/projects/{project_id}/builds/",
    )

    build_id = create_response.json()["id"]

    client.patch(
        f"/projects/{project_id}/builds/{build_id}",
        json={
            "status": "running",
        },
    )

    response = client.patch(
        f"/projects/{project_id}/builds/{build_id}",
        json={
            "status": "success",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["started_at"] is not None
    assert data["finished_at"] is not None


def test_transition_build_to_failed(client: TestClient):
    project_id = create_test_project(client)

    create_response = client.post(
        f"/projects/{project_id}/builds/",
    )

    build_id = create_response.json()["id"]

    client.patch(
        f"/projects/{project_id}/builds/{build_id}",
        json={
            "status": "running",
        },
    )

    response = client.patch(
        f"/projects/{project_id}/builds/{build_id}",
        json={
            "status": "failed",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "failed"
    assert data["started_at"] is not None
    assert data["finished_at"] is not None


def test_invalid_queued_to_success_transition(
    client: TestClient,
):
    project_id = create_test_project(client)

    create_response = client.post(
        f"/projects/{project_id}/builds/",
    )

    build_id = create_response.json()["id"]

    response = client.patch(
        f"/projects/{project_id}/builds/{build_id}",
        json={
            "status": "success",
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == "Cannot transition build from queued to success"


def test_invalid_success_to_running_transition(
    client: TestClient,
):
    project_id = create_test_project(client)

    create_response = client.post(
        f"/projects/{project_id}/builds/",
    )

    build_id = create_response.json()["id"]

    client.patch(
        f"/projects/{project_id}/builds/{build_id}",
        json={
            "status": "running",
        },
    )

    client.patch(
        f"/projects/{project_id}/builds/{build_id}",
        json={
            "status": "success",
        },
    )

    response = client.patch(
        f"/projects/{project_id}/builds/{build_id}",
        json={
            "status": "running",
        },
    )

    assert response.status_code == 400

    assert (
        response.json()["detail"] == "Cannot transition build from success to running"
    )


def test_run_build_success(client, tmp_path):
    project_id = create_test_project(client)

    response = client.post(f"/projects/{project_id}/builds/")

    assert response.status_code == 201

    build_id = response.json()["id"]

    hello_file = tmp_path / "hello.py"

    hello_file.write_text("print('Hello from ShipForge')")

    def fake_clone(repository_url, workspace):
        (workspace / "hello.py").write_text(
            "print('Hello from ShipForge')"
        )


    def fake_runner(command, workspace):
        return 0, "Hello from ShipForge\n"


    run_build(
        project_id,
        build_id,
        repository_url="https://example.com/test.git",
        command="python hello.py",
        session_factory=TestSessionLocal,
        repository_cloner=fake_clone,
        command_runner=fake_runner,
    )

    response = client.get(f"/projects/{project_id}/builds/{build_id}")

    assert response.status_code == 200

    build = response.json()

    assert build["status"] == "success"
    assert build["started_at"] is not None
    assert build["finished_at"] is not None
    db = TestSessionLocal()

    try:
        statement = select(BuildLog).where(BuildLog.build_id == build_id)

        log = db.execute(statement).scalar_one()

        assert "Hello from ShipForge" in log.output
    finally:
        db.close()


def test_create_build_log(client):
    project_id = create_test_project(client)

    response = client.post(f"/projects/{project_id}/builds/")

    assert response.status_code == 201

    build_id = response.json()["id"]

    db = TestSessionLocal()

    try:
        log = create_build_log(
            db,
            build_id,
            "Running tests...\n23 passed",
        )

        assert log.id is not None
        assert log.build_id == build_id
        assert log.output == "Running tests...\n23 passed"
        assert log.created_at is not None
    finally:
        db.close()


def test_run_build_failure(client, tmp_path):
    project_id = create_test_project(client)
    response = client.post(f"/projects/{project_id}/builds/")
    assert response.status_code == 201
    build_id = response.json()["id"]
    def fake_clone(repository_url, workspace):
        pass


    def fake_runner(command, workspace):
        return 1, "build failed\n"


    run_build(
        project_id,
        build_id,
        repository_url="https://example.com/test.git",
        command="python hello.py",
        session_factory=TestSessionLocal,
        repository_cloner=fake_clone,
        command_runner=fake_runner,
    )
    response = client.get(f"/projects/{project_id}/builds/{build_id}")
    assert response.status_code == 200
    build = response.json()
    assert build["status"] == "failed"
    assert build["started_at"] is not None
    assert build["finished_at"] is not None
    db = TestSessionLocal()
    try:
        statement = select(BuildLog).where(BuildLog.build_id == build_id)
        log = db.execute(statement).scalar_one()
        assert "build failed" in log.output
    finally:
        db.close()


def test_get_build_logs(client, tmp_path):
    project_id = create_test_project(client)

    response = client.post(f"/projects/{project_id}/builds/")

    assert response.status_code == 201

    build_id = response.json()["id"]

    hello_file = tmp_path / "hello.py"

    hello_file.write_text("print('Hello from ShipForge')")

    def fake_clone(repository_url, workspace):
        (workspace / "hello.py").write_text(
            "print('Hello from ShipForge')"
        )


    def fake_runner(command, workspace):
        return 0, "Hello from ShipForge\n"


    run_build(
        project_id,
        build_id,
        repository_url="https://example.com/test.git",
        command="python hello.py",
        session_factory=TestSessionLocal,
        repository_cloner=fake_clone,
        command_runner=fake_runner,
    )

    response = client.get(f"/projects/{project_id}/builds/{build_id}/logs")

    assert response.status_code == 200

    logs = response.json()

    assert len(logs) == 1
    assert logs[0]["build_id"] == build_id
    assert "Hello from ShipForge" in logs[0]["output"]