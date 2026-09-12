from fastapi.testclient import TestClient
from app.builds.runner import run_build
from app.database.test_database import TestSessionLocal

def create_test_project(client: TestClient) -> int:
    response = client.post(
        "/projects/",
        json={
            "name": "Build Test Project",
            "description": "Project for build tests",
        },
    )

    assert response.status_code == 201

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

def test_run_build_success(client):
    project_id = create_test_project(client)

    response = client.post(f"/projects/{project_id}/builds/")

    assert response.status_code == 201

    build_id = response.json()["id"]

    run_build(
        project_id,
        build_id,
        sleep_fn=lambda seconds: None,
        session_factory=TestSessionLocal,
    )

    response = client.get(f"/projects/{project_id}/builds/{build_id}")

    assert response.status_code == 200

    build = response.json()

    assert build["status"] == "success"
    assert build["started_at"] is not None
    assert build["finished_at"] is not None