from app.database.models import BuildLog
from sqlalchemy import select
from sqlalchemy.orm import Session


def create_build_log(
    db: Session,
    build_id: int,
    output: str,
) -> BuildLog:
    log = BuildLog(
        build_id=build_id,
        output=output,
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


def get_build_logs(
    db: Session,
    build_id: int,
) -> list[BuildLog]:
    statement = (
        select(BuildLog).where(BuildLog.build_id == build_id).order_by(BuildLog.id)
    )

    result = db.execute(statement)

    return list(result.scalars().all())
