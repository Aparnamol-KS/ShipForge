import hashlib
import hmac
import json

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

    payload = {
        "ref": "refs/heads/main",
        "after": "abc123",
        "repository": {
            "clone_url": repository_url,
        },
        "sender": {
            "login": "example-user",
        },
    }

    raw_payload = json.dumps(payload).encode()

    secret = "shipforge-webhook-secret"

    digest = hmac.new(
        secret.encode(),
        raw_payload,
        hashlib.sha256,
    ).hexdigest()

    signature = f"sha256={digest}"

    response = client.post(
        "/webhooks/github",
        content=raw_payload,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": signature,
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


def test_github_webhook_rejects_missing_signature(client):
    response = client.post(
        "/webhooks/github",
        json={
            "ref": "refs/heads/main",
            "after": "abc123",
            "repository": {
                "clone_url": "https://github.com/example/test",
            },
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid GitHub webhook signature"


def test_github_webhook_rejects_invalid_signature(client):
    payload = {
        "ref": "refs/heads/main",
        "after": "abc123",
        "repository": {
            "clone_url": "https://github.com/example/test",
        },
    }

    response = client.post(
        "/webhooks/github",
        json=payload,
        headers={
            "X-Hub-Signature-256": "sha256=invalid",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid GitHub webhook signature"