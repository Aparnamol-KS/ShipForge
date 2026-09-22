from app.builds.tasks import schedule_build
from app.redis_client.queue import BUILD_QUEUE, dequeue_build
from app.redis_client.connection import redis_client


def test_schedule_build():
    redis_client.delete(BUILD_QUEUE)

    schedule_build(
        project_id=10,
        build_id=20,
    )

    job = dequeue_build()

    assert job == {
        "build_id": 20,
        "project_id": 10,
    }
