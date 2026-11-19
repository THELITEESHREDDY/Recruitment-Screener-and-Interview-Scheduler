import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Float,
    Text,
    JSON,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column,relationship

from typing import TYPE_CHECKING


from backend.models.candidate_ranking import CandidateRanking
from backend.models.job_ranking_rubrik import JobRankingRubric
from backend.models.ideal_candidate import IdealCandidateModel

from ..db.base import Base

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    job_description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    ideal_candidate: Mapped["IdealCandidateModel"] = relationship(
        back_populates="job_description",
        uselist=False
    )

    ranking_rubric: Mapped["JobRankingRubric"] = relationship(
        back_populates="job_description",
        uselist=False
    )

    candidate_rankings: Mapped[list["CandidateRanking"]] = relationship(
        back_populates="job_description"
    )