# for subscribing to events belonging to a particular build.

import json

from app.redis_client.connection import redis_client
from app.redis_client.events import build_channel


def get_build_event(
    build_id: int,
    timeout: float = 1,
) -> dict | None:
    pubsub = redis_client.pubsub()

    channel = build_channel(build_id)

    pubsub.subscribe(channel)

    try:
        # Consume Redis subscription confirmation.
        pubsub.get_message(
            timeout=timeout,
        )

        message = pubsub.get_message(
            timeout=timeout,
        )

        if message is None:
            return None

        if message["type"] != "message":
            return None

        return json.loads(message["data"])

    finally:
        pubsub.close()