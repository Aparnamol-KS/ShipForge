def test_github_webhook_creates_build(client):
    repository_url = "https://github.com/example/webhook-build"

    project_response = client.post(
        "/projects/",
        json={
            "name": "Webhook Build Project",
            "description": "Testing webhook build creation",
            "repository_url": repository_url,
            "build_command": "pytest",
        },
    )

    assert project_response.status_code == 201

    project = project_response.json()

    response = client.post(
        "/webhooks/github",
        json={
            "ref": "refs/heads/main",
            "after": "abc123",
            "repository": {
                "clone_url": repository_url,
            },
            "sender": {
                "login": "example-user",
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Build queued"
    assert data["project_id"] == project["id"]
    assert data["project_name"] == "Webhook Build Project"
    assert data["build_number"] == 1
    assert data["status"] == "queued"
    assert data["repository_url"] == repository_url
    assert data["branch"] == "refs/heads/main"
    assert data["commit_sha"] == "abc123"
