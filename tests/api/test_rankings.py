from fastapi.testclient import TestClient

from backend.main import app
from backend.db.connection import get_db
from backend.core.dependencies import get_current_user

from backend.models.users import User
from backend.models.job import JobDescription
from backend.models.candidate import Candidate
from backend.models.candidate_ranking import CandidateRanking


def test_get_job_rankings(db_setup):
    recruiter = User(
        email="rankings@example.com",
        password_hash="hashed-password",
    )

    db_setup.add(recruiter)
    db_setup.flush()

    job = JobDescription(
        job_description="Python Backend Engineer",
        user_id=recruiter.id,
    )

    db_setup.add(job)
    db_setup.flush()

    candidate = Candidate(
        name="Alice",
        email="alice@example.com",
        mobile_number="1234567890",
        google_form_response_id="ranking-test-001",
    )

    db_setup.add(candidate)
    db_setup.flush()

    ranking = CandidateRanking(
        jd_id=job.id,
        candidate_id=candidate.id,
        overall_score=94.5,
        secondary_score=88.0,
        match_scores={},
        secondary_details={},
        rank=1,
        one_line_rationale="Strong technical alignment",
    )

    db_setup.add(ranking)
    db_setup.commit()

    def override_get_db():
        yield db_setup

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: recruiter

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/jobs/{job.id}/rankings"
            )

        assert response.status_code == 200

        data = response.json()

        assert data["job_id"] == job.id
        assert data["total_candidates"] == 1
        assert len(data["rankings"]) == 1

        assert data["rankings"][0]["candidate_name"] == "Alice"
        assert data["rankings"][0]["rank"] == 1
        assert data["rankings"][0]["overall_score"] == 94.5

    finally:
        app.dependency_overrides.clear()


def test_recruiter_cannot_access_another_recruiters_rankings(db_setup):
    recruiter_a = User(
        email="recruiter-a@example.com",
        password_hash="hashed-password",
    )

    recruiter_b = User(
        email="recruiter-b@example.com",
        password_hash="hashed-password",
    )

    db_setup.add_all([recruiter_a, recruiter_b])
    db_setup.flush()

    job_b = JobDescription(
        job_description="Backend Engineer",
        user_id=recruiter_b.id,
    )

    db_setup.add(job_b)
    db_setup.commit()

    def override_get_db():
        yield db_setup

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: recruiter_a

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/jobs/{job_b.id}/rankings"
            )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()