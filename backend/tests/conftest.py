import pytest
from fastapi.testclient import TestClient

from app.database.connection import Base, get_db
from app.database.models import Project
from app.database.test_database import TestSessionLocal, test_engine
from app.main import app

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv(
        "GITHUB_WEBHOOK_SECRET",
        "shipforge-webhook-secret",
    )

    # Whenever the router tries to schedule a build during a test, do nothing
    monkeypatch.setattr(
        "app.builds.router.schedule_build",
        lambda *args, **kwargs: None,
    )

    # webhook test shouldn't actually clone a repository and start Docker
    monkeypatch.setattr(
        "app.webhooks.github.schedule_build",
        lambda *args, **kwargs: None,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)