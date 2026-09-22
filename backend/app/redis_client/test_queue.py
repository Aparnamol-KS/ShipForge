from app.redis_client.queue import (
    BUILD_QUEUE,
    dequeue_build,
    enqueue_build,
)
from app.redis_client.connection import redis_client


def test_build_queue():
    redis_client.delete(BUILD_QUEUE)

    enqueue_build(
        build_id=123,
        project_id=456,
    )

    job = dequeue_build()

    assert job == {
        "build_id": 123,
        "project_id": 456,
    }
