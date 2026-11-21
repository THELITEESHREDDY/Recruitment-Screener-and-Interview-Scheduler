from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.connection import get_db
from backend.models.job import JobDescription
from backend.models.candidate import Candidate
from backend.models.candidate_ranking import CandidateRanking
from backend.schemas.scheduling import InterviewWindow, WorkingHours
from backend.services.scheduling import create_interview_schedule


router = APIRouter(prefix="/jobs", tags=["Scheduling"])





class SchedulingRequest(BaseModel):
    mode: Literal["explicit", "automatic"]
    top_n: int = Field(default=3, ge=1)
    interview_duration_minutes: int = Field(ge=1)

    schedule: list[InterviewWindow] | None = None
    start_date: str | None = None
    daily_working_hours: WorkingHours | None = None

    @model_validator(mode="after")
    def validate_mode_fields(self):
        if self.mode == "explicit":
            if not self.schedule:
                raise ValueError(
                    "Explicit scheduling requires schedule"
                )
        else:
            if not self.start_date or not self.daily_working_hours:
                raise ValueError(
                    "Automatic scheduling requires start_date "
                    "and daily_working_hours"
                )

        return self


@router.post("/{job_id}/schedule")
def schedule_interviews(
    job_id: str,
    request: SchedulingRequest,
    db: Session = Depends(get_db)
):
    job = db.get(JobDescription, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    rankings = db.scalars(
        select(CandidateRanking)
        .where(CandidateRanking.jd_id == job_id)
        .order_by(
            CandidateRanking.rank,
            CandidateRanking.overall_score.desc(),
            CandidateRanking.candidate_id
        )
    ).all()

    if not rankings:
        raise HTTPException(
            status_code=400,
            detail="No ranked candidates available"
        )

    ranked_candidates = []

    for ranking in rankings:
        candidate = db.get(Candidate, ranking.candidate_id)

        if candidate is None:
            continue

        ranked_candidates.append({
            "candidate_id": candidate.id,
            "candidate_name": candidate.name,
            "rank": ranking.rank,
            "overall_score": ranking.overall_score
        })

    config = request.model_dump(mode="json", exclude_none=True)

    try:
        return create_interview_schedule(
            ranked_candidates=ranked_candidates,
            config=config
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc