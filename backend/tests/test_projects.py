from app.database.test_database import TestSessionLocal
from app.projects.service import get_project_by_repository

def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_project(client):
    response = client.post(
        "/projects/",
        json={
            "name": "Test Project",
            "description": "Created by pytest",
            "repository_url": "https://github.com/example/test-project",
            "build_command": "pytest",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Project"
    assert data["description"] == "Created by pytest"
    assert data["repository_url"] == "https://github.com/example/test-project"
    assert data["build_command"] == "pytest"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_get_projects(client):
    client.post(
        "/projects/",
        json={
            "name": "Project One",
            "description": "First test project",
            "repository_url": "https://github.com/example/project-one",
            "build_command": "pytest",
        },
    )

    client.post(
        "/projects/",
        json={
            "name": "Project Two",
            "description": "Second test project",
            "repository_url": "https://github.com/example/project-two",
            "build_command": "pytest",
        },
    )

    response = client.get("/projects/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Project One"
    assert data[1]["name"] == "Project Two"


def test_get_project(client):
    create_response = client.post(
        "/projects/",
        json={
            "name": "Single Project",
            "description": "Testing single project retrieval",
            "repository_url": "https://github.com/example/single",
            "build_command": "pytest",
        },
    )

    project_id = create_response.json()["id"]

    response = client.get(f"/projects/{project_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == project_id
    assert data["name"] == "Single Project"


def test_get_project_not_found(client):
    response = client.get("/projects/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


def test_get_project_by_repository(client):
    repository_url = "https://github.com/example/repository-test"

    response = client.post(
        "/projects/",
        json={
            "name": "Repository Test Project",
            "description": "Testing repository lookup",
            "repository_url": repository_url,
            "build_command": "pytest",
        },
    )

    assert response.status_code == 201

    db = TestSessionLocal()

    try:
        project = get_project_by_repository(
            db,
            repository_url,
        )

        assert project is not None
        assert project.name == "Repository Test Project"
        assert project.repository_url == repository_url

    finally:
        db.close()



def test_get_project_by_repository_not_found(client):
    db = TestSessionLocal()

    try:
        project = get_project_by_repository(
            db,
            "https://github.com/example/does-not-exist",
        )

        assert project is None

    finally:
        db.close()



def test_update_project(client):
    create_response = client.post(
        "/projects/",
        json={
            "name": "Original Name",
            "description": "Original description",
            "repository_url": "https://github.com/example/original",
            "build_command": "pytest",
        },
    )

    project_id = create_response.json()["id"]

    response = client.patch(
        f"/projects/{project_id}",
        json={
            "name": "Updated Name",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == project_id
    assert data["name"] == "Updated Name"
    assert data["description"] == "Original description"
    assert data["repository_url"] == "https://github.com/example/original"
    assert data["build_command"] == "pytest"


def test_update_project_not_found(client):
    response = client.patch(
        "/projects/999999",
        json={
            "name": "Does Not Exist",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


def test_delete_project(client):
    create_response = client.post(
        "/projects/",
        json={
            "name": "Project To Delete",
            "description": "This project will be deleted",
            "repository_url": "https://github.com/example/delete",
            "build_command": "pytest",
        },
    )

    project_id = create_response.json()["id"]

    response = client.delete(f"/projects/{project_id}")

    assert response.status_code == 200
    assert response.json() == {"message": "Project deleted successfully"}

    get_response = client.get(f"/projects/{project_id}")

    assert get_response.status_code == 404


def test_delete_project_not_found(client):
    response = client.delete("/projects/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}
