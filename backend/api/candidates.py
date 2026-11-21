from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.db.connection import get_db
from backend.integrations.candidate_ingestion import fetch_candidates
from backend.integrations.pipeline_adapter import adapt_candidates_for_pipeline
from backend.models.job import JobDescription
from backend.utils.google_sheets import extract_spreadsheet_id


router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"]
)


@router.post("/sync/{job_id}")
def sync_candidates(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Fetch candidates from the Google Sheet
    associated with the given job.
    """

    # 1. Retrieve job
    job = db.get(JobDescription, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    # 2. Check spreadsheet configuration
    if not job.spreadsheet_url:
        raise HTTPException(
            status_code=400,
            detail="No Google Sheet configured for this job"
        )

    # 3. Extract spreadsheet ID
    try:
        spreadsheet_id = extract_spreadsheet_id(
            job.spreadsheet_url
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc

    # 4. Fetch candidates
    candidates = fetch_candidates(spreadsheet_id)

    # 5. Prepare candidates for pipeline
    pipeline_candidates = adapt_candidates_for_pipeline(
        candidates
    )

    return {
        "total_candidates": len(pipeline_candidates),
        "candidates": [
            {
                "candidate_id": candidate["candidate_id"],
                "filename": candidate["pdf"].filename,
                "pep_score": candidate["pep_score"],
                "pep_priority": candidate["pep_priority"]
            }
            for candidate in pipeline_candidates
        ]
    }