import hashlib
import hmac
import json
from app.database.test_database import TestSessionLocal
from app.database.models import Build

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
            "X-GitHub-Event": "push",
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
    assert data["branch"] == "main"
    assert data["commit_sha"] == "abc123"

    db = TestSessionLocal()


    try:
        build = db.query(Build).filter(Build.id == data["build_id"]).first()

        assert build is not None
        assert build.branch == "main"
        assert build.commit_sha == "abc123"

    finally:
        db.close()


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


def test_github_webhook_allows_install_and_test_without_build_command(client):
    repository_url = "https://github.com/example/webhook-pipeline"

    project_response = client.post(
        "/projects/",
        json={
            "name": "Webhook Pipeline Project",
            "repository_url": repository_url,
            "install_command": "cd backend && uv sync --dev",
            "test_command": "cd backend && uv run pytest -q",
        },
    )

    assert project_response.status_code == 201

    payload = {
        "ref": "refs/heads/main",
        "after": "def456",
        "repository": {
            "clone_url": repository_url,
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
            "X-GitHub-Event": "push",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Build queued"
    assert data["status"] == "queued"

def test_github_webhook_ignores_non_push_event(client):
    payload = {
        "ref": "refs/heads/main",
        "after": "abc123",
        "repository": {
            "clone_url": "https://github.com/example/test",
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
            "X-GitHub-Event": "pull_request",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Webhook event ignored"
    assert data["event"] == "pull_request"