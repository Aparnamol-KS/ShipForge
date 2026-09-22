"""
- publishing a build event to Redis
- subscribing to events for a particular build

Pub/Sub:

Worker → Redis → all interested subscribers

An event is broadcast to whoever is listening.
"""


import json

from app.redis_client.connection import redis_client


def build_channel(build_id: int) -> str:
    return f"shipforge:build:{build_id}"


def publish_build_event(
    build_id: int,
    event: dict,
) -> None:
    channel = build_channel(build_id)

    redis_client.publish(
        channel,
        json.dumps(event),
    )