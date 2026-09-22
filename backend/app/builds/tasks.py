from app.redis_client.queue import enqueue_build


def schedule_build(
    project_id: int,
    build_id: int,
) -> None:
    enqueue_build(
        build_id=build_id,
        project_id=project_id,
    )
