# models/job_ranking_rubric.py
from typing import TYPE_CHECKING
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    JSON,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from backend.models.job import JobDescription
from ..db.base import Base


class JobRankingRubric(Base):
    __tablename__ = "job_ranking_rubrics"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    jd_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("job_descriptions.id"),
        unique=True,
        nullable=False,
        index=True
    )

    criteria: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    job_description: Mapped["JobDescription"] = relationship(
        back_populates="ranking_rubric"
    )