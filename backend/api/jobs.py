from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException

from backend.db.connection import get_db
from backend.models.job import JobDescription
from backend.schemas.job import JobCreate, JobResponse
from backend.utils.google_sheets import extract_spreadsheet_id


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)

@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED
)
def create_job(
    payload: JobCreate,
    db: Session = Depends(get_db)
):
    spreadsheet_url = payload.spreadsheet_url.strip()

    
    if not spreadsheet_url:
        raise HTTPException(
            status_code=422,
            detail="Google Sheets URL cannot be empty"
        )

    try:
        extract_spreadsheet_id(spreadsheet_url)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc

    job = JobDescription(
        job_description=payload.job_description,
        spreadsheet_url=spreadsheet_url
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job



@router.get(
    "",
    response_model=list[JobResponse]
)
def get_jobs(db: Session = Depends(get_db)):
    statement = select(JobDescription)
    jobs = db.scalars(statement).all()

    return jobs



@router.get(
    "/{job_id}",
    response_model=JobResponse
)
def get_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    job = db.get(JobDescription, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job