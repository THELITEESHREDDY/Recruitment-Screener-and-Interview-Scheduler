import os

from fastapi import APIRouter, HTTPException

from backend.integrations.candidate_ingestion import fetch_candidates
from backend.integrations.pipeline_adapter import adapt_candidates_for_pipeline


router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"]
)


@router.post("/sync")
def sync_candidates():
    """
    Fetch Google Forms candidates and prepare
    them for the recruitment pipeline.
    """

    spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID")

    if not spreadsheet_id:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_SPREADSHEET_ID is not configured"
        )

    candidates = fetch_candidates(spreadsheet_id)

    pipeline_candidates = adapt_candidates_for_pipeline(candidates)

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