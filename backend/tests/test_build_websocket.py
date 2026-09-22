import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.builds.websocket import manager


def test_build_websocket_connection():
    client = TestClient(app)

    with client.websocket_connect("/projects/1/builds/1/ws") as websocket:
        assert websocket is not None

# lets pytest execute the test in an async context.

@pytest.mark.anyio
async def test_build_websocket_broadcast():
    class FakeWebSocket:
        def __init__(self):
            self.messages = []

        async def send_json(self, message):
            self.messages.append(message)

    websocket = FakeWebSocket()

    manager.active_connections[1] = [websocket]

    try:
        await manager.broadcast(
            1,
            {
                "type": "status",
                "status": "running",
            },
        )

        assert websocket.messages == [
            {
                "type": "status",
                "status": "running",
            }
        ]

    finally:
        manager.active_connections.pop(1, None)
