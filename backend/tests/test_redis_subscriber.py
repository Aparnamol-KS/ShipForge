import threading
import time

from app.redis_client.events import publish_build_event
from app.redis_client.subscriber import get_build_event


def test_get_build_event():
    build_id = 54321

    result = {}

    def subscriber():
        result["event"] = get_build_event(
            build_id,
            timeout=5,
        )

    thread = threading.Thread(
        target=subscriber,
    )

    thread.start()

    time.sleep(0.2)

    event = {
        "type": "status",
        "status": "running",
    }

    publish_build_event(
        build_id,
        event,
    )

    thread.join(
        timeout=5,
    )

    assert not thread.is_alive()
    assert result["event"] == event
