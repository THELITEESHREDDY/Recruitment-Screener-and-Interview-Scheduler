# models/candidate_ranking.py

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Float,
    Integer,
    Text,
    JSON,
    DateTime,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.models.candidate import Candidate
    from backend.models.job import JobDescription

from ..db.base import Base


class CandidateRanking(Base):
    __tablename__ = "candidate_rankings"

    __table_args__ = (
        UniqueConstraint(
            "jd_id",
            "candidate_id",
            name="uq_candidate_ranking_jd_candidate"
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    jd_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("job_descriptions.id"),
        nullable=False,
        index=True
    )

    candidate_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("candidates.id"),
        nullable=False,
        index=True
    )

    overall_score: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    match_scores: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
    )

    secondary_score: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    secondary_details: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
    )

    rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    one_line_rationale: Mapped[str] = mapped_column(
        Text,
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
        back_populates="candidate_rankings"
    )

    candidate: Mapped["Candidate"] = relationship(
        back_populates="ranking"
    )