from datetime import datetime, timezone
from enum import Enum as PyEnum

from app.database.connection import Base
from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    repository_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    build_command: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    install_command: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    test_command: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class BuildStatus(str, PyEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

class BuildStage(str, PyEnum):
    INSTALL = "install"
    TEST = "test"
    BUILD = "build"

class Build(Base):
    __tablename__ = "builds"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "build_number",
            name="uq_build_project_number",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
    )

    build_number: Mapped[int] = mapped_column(
        nullable=False,
    )

    status: Mapped[BuildStatus] = mapped_column(
        SQLEnum(BuildStatus),
        default=BuildStatus.QUEUED,
        nullable=False,
    )

    stage: Mapped[BuildStage | None] = mapped_column(
        SQLEnum(BuildStage),
        nullable=True,
    )
    
    branch: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    commit_sha: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class BuildLog(Base):
    __tablename__ = "build_logs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    build_id: Mapped[int] = mapped_column(
        ForeignKey("builds.id"),
        nullable=False,
    )

    output: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )