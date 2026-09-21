import hashlib
import hmac
import json

from app.webhooks.security import verify_github_signature


def test_valid_github_signature():
    repository_url = "https://github.com/example/webhook-build"

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

    assert verify_github_signature(
        raw_payload,
        signature,
        secret,
    )


def test_invalid_github_signature():
    payload = b'{"hello": "world"}'
    secret = "test-secret"

    signature = "sha256=invalid"

    assert not verify_github_signature(
        payload,
        signature,
        secret,
    )


def test_missing_github_signature():
    payload = b'{"hello": "world"}'
    secret = "test-secret"

    assert not verify_github_signature(
        payload,
        None,
        secret,
    )


