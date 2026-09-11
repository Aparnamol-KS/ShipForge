from fastapi.testclient import TestClient


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