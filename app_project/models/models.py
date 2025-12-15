from datetime import datetime
from typing import Optional

from sqlalchemy import TIMESTAMP, JSON, TEXT, String, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from app_project.database import Base
from enum import Enum as PyEnum


class Status(str, PyEnum):
    NEW = "new"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "CANCELLED"


class Priority(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Tasks(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(TEXT, nullable=False)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), default=Priority.LOW)
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.PENDING)
    created_at: Mapped[datetime] = mapped_column(server_default=func.timezone('utc', func.now()), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), default=None, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), default=None, nullable=True)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    errors: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)
