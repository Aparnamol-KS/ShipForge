import json

from app.redis_client.connection import redis_client

BUILD_QUEUE = "shipforge:builds"


def enqueue_build(build_id: int, project_id: int) -> None:
    job = {
        "build_id": build_id,
        "project_id": project_id,
    }
    # Add to the right/end of a Redis list.
    redis_client.rpush(
        BUILD_QUEUE,
        json.dumps(job),
    )


def dequeue_build() -> dict | None:
    job = redis_client.lpop(BUILD_QUEUE)

    if job is None:
        return None

    return json.loads(job)


def wait_for_build(
    timeout: int = 1,
) -> dict | None:
    result = redis_client.blpop(
        BUILD_QUEUE,
        timeout=timeout,
    )

    if result is None:
        return None

    _, job = result

    return json.loads(job)