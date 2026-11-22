from sqlalchemy import update

from backend.db.connection import LocalSession
from backend.models.job import JobDescription
import backend.db.init_db

def assign_legacy_jobs(user_id: str):
    with LocalSession() as db:
        result = db.execute(
            update(JobDescription)
            .where(JobDescription.user_id.is_(None))
            .values(user_id=user_id)
        )

        db.commit()

        print(
            f"Assigned {result.rowcount} legacy jobs "
            f"to user {user_id}"
        )


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python -m scripts.assign_legacy_jobs <user_id>"
        )

    assign_legacy_jobs(sys.argv[1])