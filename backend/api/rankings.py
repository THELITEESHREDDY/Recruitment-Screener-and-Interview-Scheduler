from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.connection import get_db
from backend.models.job import JobDescription
from backend.models.candidate import Candidate
from backend.models.candidate_ranking import CandidateRanking
from backend.core.job_dependency import get_owned_job


router = APIRouter(prefix="/jobs", tags=["Rankings"])


@router.get("/{job_id}/rankings")
def get_job_rankings(
    job_id: str,
    db: Session = Depends(get_db),
    job: JobDescription = Depends(get_owned_job),
):
    rankings = db.scalars(
        select(CandidateRanking)
        .where(CandidateRanking.jd_id == job.id)
        .order_by(
            CandidateRanking.rank,
            CandidateRanking.overall_score.desc(),
            CandidateRanking.candidate_id,
        )
    ).all()

    results = []

    for ranking in rankings:
        candidate = db.get(Candidate, ranking.candidate_id)

        if candidate is None:
            continue

        results.append({
            "candidate_id": candidate.id,
            "candidate_name": candidate.name,
            "email": candidate.email,
            "mobile_number": candidate.mobile_number,
            "linkedin_url": candidate.linkedin_url,
            "rank": ranking.rank,
            "overall_score": ranking.overall_score,
            "secondary_score": ranking.secondary_score,
            "one_line_rationale": ranking.one_line_rationale,
            "match_scores": ranking.match_scores,
            "secondary_details": ranking.secondary_details,
        })

    return {
        "job_id": job.id,
        "total_candidates": len(results),
        "rankings": results,
    }