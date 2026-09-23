import asyncio

from app.builds.event_listener import forward_build_events
from app.redis_client.events import publish_build_event


class FakeWebSocket:
    def __init__(self):
        self.messages = []

    async def send_json(self, message):
        self.messages.append(message)


def test_forward_build_events():
    build_id = 67890
    websocket = FakeWebSocket()

    async def run_test():
        listener_task = asyncio.create_task(
            forward_build_events(
                build_id,
                websocket,
            )
        )

        await asyncio.sleep(0.2)

        event = {
            "type": "status",
            "status": "running",
        }

        publish_build_event(
            build_id,
            event,
        )

        await asyncio.sleep(0.5)

        listener_task.cancel()

        try:
            await listener_task
        except asyncio.CancelledError:
            pass

        assert websocket.messages == [event]

    asyncio.run(run_test())
