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
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class IdealCandidateModel(Base):
    __tablename__ = "ideal_candidates"

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

    technical_skills: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False
    )

    soft_skills: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False
    )

    tech_stacks: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False
    )

    tools_and_platforms: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False
    )

    certifications: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False
    )

    work_experience: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False
    )

    coursework: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False
    )

    achievements: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False
    )

    education: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    mandatory_requirements: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False
    )

    preferred_requirements: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False
    )

    minimum_experience_years: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    required_education_level: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    evaluation_weights: Mapped[dict[str, float]] = mapped_column(
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