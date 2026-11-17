# models/candidate.py

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from backend.models.candidate_ranking import CandidateRanking
from ..db.base import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    mobile_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    linkedin_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    google_form_response_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    ranking: Mapped["CandidateRanking"] = relationship(
        back_populates="candidate",
        uselist=False
    )