import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.connection import get_db
from backend.models.job import JobDescription

from backend.integrations.candidate_ingestion import fetch_candidates
from backend.integrations.pipeline_adapter import adapt_candidates_for_pipeline

from agents.pipeline import run_recruitment_pipeline
from sqlalchemy import select
from backend.models.candidate_ranking import CandidateRanking
from backend.utils.google_sheets import extract_spreadsheet_id
from backend.core.job_dependency import get_owned_job
from backend.models.job import JobDescription

router = APIRouter(
    prefix="/jobs",
    tags=["Screening"]
)


@router.post("/{job_id}/screen")
async def screen_candidates(
    job_id: str,
    top_n: int = 3,
    db: Session = Depends(get_db),
    job: JobDescription = Depends(get_owned_job)
):
    if top_n < 1:
        raise HTTPException(
            status_code=422,
            detail="top_n must be at least 1"
        )

   

    # 2. Get Google Spreadsheet ID
    if not job.spreadsheet_url:
        raise HTTPException(
            status_code=400,
            detail="No Google Sheet configured for this job"
        )

    try:
        spreadsheet_id = extract_spreadsheet_id(
            job.spreadsheet_url
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc

    # 3. Fetch candidate responses and resume PDFs
    candidates = fetch_candidates(spreadsheet_id)

    if not candidates:
        raise HTTPException(
            status_code=400,
            detail="No candidates found in Google Sheets"
        )

    # 4. Convert candidates into pipeline inputs
    pipeline_candidates = adapt_candidates_for_pipeline(
        candidates
    )

    # Find candidates already screened for this job
    existing_candidate_ids = set(
        db.scalars(
            select(CandidateRanking.candidate_id).where(
                CandidateRanking.jd_id == job_id
            )
        ).all()
    )

    # Only process candidates without an existing ranking
    new_candidates = [
        candidate
        for candidate in pipeline_candidates
        if candidate["candidate_id"] not in existing_candidate_ids
    ]

    if not new_candidates:
        return {
            "message": "All candidates have already been screened for this job",
            "new_candidates": 0
        }
    
        # 5. Execute recruitment pipeline
    result = await run_recruitment_pipeline(
        jd_id=job.id,
        job_description=job.job_description,
        candidates=new_candidates,
        top_n=top_n
    )

    return result