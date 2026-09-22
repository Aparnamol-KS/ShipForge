import json

from app.redis_client.connection import redis_client
from app.redis_client.events import (
    build_channel,
    publish_build_event,
)


def test_publish_build_event():
    build_id = 12345
    channel = build_channel(build_id)

    pubsub = redis_client.pubsub()
    pubsub.subscribe(channel)

    # Redis sends a subscription confirmation first.
    subscription_message = pubsub.get_message(
        timeout=1,
    )

    assert subscription_message is not None
    assert subscription_message["type"] == "subscribe"

    event = {
        "type": "status",
        "status": "running",
    }

    publish_build_event(
        build_id,
        event,
    )

    message = pubsub.get_message(
        timeout=1,
    )

    try:
        assert message is not None
        assert message["type"] == "message"
        assert message["channel"] == channel

        received_event = json.loads(message["data"])

        assert received_event == event

    finally:
        pubsub.close()
