from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.connection import get_db
from backend.models.job import JobDescription
from backend.models.candidate import Candidate
from backend.models.candidate_ranking import CandidateRanking
from backend.schemas.scheduling import SchedulingRequest
from backend.services.scheduling import create_interview_schedule
from backend.core.job_dependency import get_owned_job

router = APIRouter(prefix="/jobs", tags=["Scheduling"])








@router.post("/{job_id}/schedule")
def schedule_interviews(
    job_id: str,
    request: SchedulingRequest,
    db: Session = Depends(get_db),
    job: JobDescription = Depends(get_owned_job)
):
  

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