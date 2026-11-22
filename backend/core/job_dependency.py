from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.db.connection import get_db
from backend.models.job import JobDescription
from backend.models.users import User


def get_owned_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> JobDescription:

    job = db.scalar(
        select(JobDescription).where(
            JobDescription.id == job_id,
            JobDescription.user_id == current_user.id
        )
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job