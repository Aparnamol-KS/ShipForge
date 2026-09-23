from app.builds.runner import run_build
from app.database.connection import SessionLocal
from app.database.models import Build, Project
from app.redis_client.queue import wait_for_build
from app.redis_client.events import publish_build_event

def run_worker(
    once: bool = False,
    session_factory=SessionLocal,
) -> None:
    print("ShipForge worker started.")

    while True:
        job = wait_for_build(timeout=1)

        if job is None:
            if once:
                break

            continue

        build_id = job["build_id"]
        project_id = job["project_id"]

        db = session_factory()

        try:
            project = db.get(Project, project_id)
            build = db.get(Build, build_id)

            if project is None:
                print(f"Project {project_id} not found.")
                continue

            if build is None:
                print(f"Build {build_id} not found.")
                continue

            if not project.repository_url:
                print(f"Project {project_id} has no repository URL.")
                continue

            if not project.build_command:
                print(f"Project {project_id} has no build command.")
                continue

            print(f"Starting build #{build.build_number} for project {project.name}")

            run_build(
                project_id=project_id,
                build_id=build_id,
                repository_url=project.repository_url,
                command=project.build_command,
                session_factory=session_factory,
                event_publisher=publish_build_event,
            )

        finally:
            db.close()

        if once:
            break


if __name__ == "__main__":
    run_worker()
