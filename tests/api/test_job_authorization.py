from fastapi.testclient import TestClient

from backend.main import app
from fastapi import Depends
from backend.db.connection import get_db
from backend.core.dependencies import get_current_user
from backend.models.users import User
from backend.models.job import JobDescription
from backend.core.security import create_access_token
import jwt
from datetime import datetime, timedelta, timezone

client = TestClient(app)


def test_create_job_without_authentication():
    response = client.post(
        "/jobs",
        json={
            "job_description": "Python Backend Engineer",
            "spreadsheet_url": (
                "https://docs.google.com/spreadsheets/d/"
                "test_spreadsheet_id/edit"
            )
        }
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Invalid or expired authentication token"
    }

def test_recruiter_cannot_access_another_recruiters_job(
    db_setup,
    monkeypatch
):
    # Create two recruiters in the isolated test database
    recruiter_a = User(
        email="recruiter_a@example.com",
        password_hash="test_hash"
    )

    recruiter_b = User(
        email="recruiter_b@example.com",
        password_hash="test_hash"
    )

    db_setup.add_all([recruiter_a, recruiter_b])
    db_setup.commit()

    db_setup.refresh(recruiter_a)
    db_setup.refresh(recruiter_b)

    # Create a job owned by Recruiter B
    job_b = JobDescription(
        job_description="Python Backend Engineer",
        spreadsheet_url=(
            "https://docs.google.com/spreadsheets/d/"
            "test_spreadsheet_id/edit"
        ),
        user_id=recruiter_b.id
    )

    db_setup.add(job_b)
    db_setup.commit()
    db_setup.refresh(job_b)

    # Override dependencies for the API test
    def override_get_db():
        yield db_setup

    def override_get_current_user():
        return recruiter_a

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        with TestClient(app) as test_client:
            response = test_client.get(
                f"/jobs/{job_b.id}"
            )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Job not found"
        }

    finally:
        app.dependency_overrides.clear()

def test_recruiter_sees_only_own_jobs(db_setup):
    recruiter_a = User(
        email="recruiter_a@example.com",
        password_hash="test_hash"
    )

    recruiter_b = User(
        email="recruiter_b@example.com",
        password_hash="test_hash"
    )

    db_setup.add_all([recruiter_a, recruiter_b])
    db_setup.commit()

    job_a = JobDescription(
        job_description="Backend Engineer",
        spreadsheet_url="https://docs.google.com/spreadsheets/d/sheet_a/edit",
        user_id=recruiter_a.id
    )

    job_b = JobDescription(
        job_description="Frontend Engineer",
        spreadsheet_url="https://docs.google.com/spreadsheets/d/sheet_b/edit",
        user_id=recruiter_b.id
    )

    db_setup.add_all([job_a, job_b])
    db_setup.commit()

    def override_get_db():
        yield db_setup

    def override_get_current_user():
        return recruiter_a

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        with TestClient(app) as test_client:
            response = test_client.get("/jobs")

        assert response.status_code == 200

        jobs = response.json()

        assert len(jobs) == 1
        assert jobs[0]["id"] == job_a.id
        assert jobs[0]["job_description"] == "Backend Engineer"

        assert all(
            job["id"] != job_b.id
            for job in jobs
        )

    finally:
        app.dependency_overrides.clear()


def test_recruiter_cannot_screen_another_recruiters_job(
    db_setup,
    monkeypatch
):
    from backend.api import screening

    recruiter_a = User(
        email="recruiter_a@example.com",
        password_hash="test_hash"
    )

    recruiter_b = User(
        email="recruiter_b@example.com",
        password_hash="test_hash"
    )

    db_setup.add_all([recruiter_a, recruiter_b])
    db_setup.commit()

    job_b = JobDescription(
        job_description="AI Engineer",
        spreadsheet_url=(
            "https://docs.google.com/spreadsheets/d/"
            "test_spreadsheet_id/edit"
        ),
        user_id=recruiter_b.id
    )

    db_setup.add(job_b)
    db_setup.commit()
    db_setup.refresh(job_b)

    # Any attempt to fetch candidates should fail the test.
    def forbidden_fetch(*args, **kwargs):
        raise AssertionError(
            "Unauthorized screening accessed Google Sheets"
        )

    monkeypatch.setattr(
        screening,
        "fetch_candidates",
        forbidden_fetch
    )

    def override_get_db():
        yield db_setup

    def override_get_current_user():
        return recruiter_a

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        with TestClient(app) as test_client:
            response = test_client.post(
                f"/jobs/{job_b.id}/screen",
                params={"top_n": 3}
            )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Job not found"
        }

    finally:
        app.dependency_overrides.clear()



def test_recruiter_cannot_schedule_another_recruiters_job(
    db_setup,
    monkeypatch
):
    from backend.api import scheduling

    recruiter_a = User(
        email="recruiter_a@example.com",
        password_hash="test_hash"
    )

    recruiter_b = User(
        email="recruiter_b@example.com",
        password_hash="test_hash"
    )

    db_setup.add_all([recruiter_a, recruiter_b])
    db_setup.commit()

    job_b = JobDescription(
        job_description="Backend Engineer",
        spreadsheet_url=(
            "https://docs.google.com/spreadsheets/d/"
            "test_spreadsheet_id/edit"
        ),
        user_id=recruiter_b.id
    )

    db_setup.add(job_b)
    db_setup.commit()
    db_setup.refresh(job_b)

    # Scheduling must never execute for an unauthorized user.
    def forbidden_schedule(*args, **kwargs):
        raise AssertionError(
            "Unauthorized user triggered interview scheduling"
        )

    monkeypatch.setattr(
        scheduling,
        "create_interview_schedule",
        forbidden_schedule
    )

    def override_get_db():
        yield db_setup

    def override_get_current_user():
        return recruiter_a

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        with TestClient(app) as test_client:
            response = test_client.post(
                f"/jobs/{job_b.id}/schedule",
                json={
                    "mode": "automatic",
                    "top_n": 3,
                    "interview_duration_minutes": 15,
                    "schedule": [],
                    "start_date": "2026-11-23",
                    "daily_working_hours": {
                        "start_time": "09:00",
                        "end_time": "17:00"
                    }
                }
            )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Job not found"
        }

    finally:
        app.dependency_overrides.clear()


def test_recruiter_cannot_sync_another_recruiters_candidates(
    db_setup,
    monkeypatch
):
    from backend.api import candidates

    recruiter_a = User(
        email="recruiter_a@example.com",
        password_hash="test_hash"
    )

    recruiter_b = User(
        email="recruiter_b@example.com",
        password_hash="test_hash"
    )

    db_setup.add_all([recruiter_a, recruiter_b])
    db_setup.commit()

    job_b = JobDescription(
        job_description="AI Engineer",
        spreadsheet_url=(
            "https://docs.google.com/spreadsheets/d/"
            "test_spreadsheet_id/edit"
        ),
        user_id=recruiter_b.id
    )

    db_setup.add(job_b)
    db_setup.commit()
    db_setup.refresh(job_b)

    # Google Sheets must never be accessed for another user's job.
    def forbidden_fetch(*args, **kwargs):
        raise AssertionError(
            "Unauthorized candidate synchronization accessed Google Sheets"
        )

    monkeypatch.setattr(
        candidates,
        "fetch_candidates",
        forbidden_fetch
    )

    def override_get_db():
        yield db_setup

    def override_get_current_user():
        return recruiter_a

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        with TestClient(app) as test_client:
            response = test_client.post(
                f"/candidates/sync/{job_b.id}"
            )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Job not found"
        }

    finally:
        app.dependency_overrides.clear()


def test_access_job_with_valid_jwt(
    db_setup,
    monkeypatch
):
    from shared import config
    from backend.db.connection import get_db

    monkeypatch.setenv(
        "JWT_SECRET_KEY",
        "test-secret-key-for-jwt-authentication"
    )

    recruiter = User(
        email="recruiter@example.com",
        password_hash="test_hash"
    )

    db_setup.add(recruiter)
    db_setup.commit()
    db_setup.refresh(recruiter)

    job = JobDescription(
        job_description="Backend Engineer",
        spreadsheet_url=(
            "https://docs.google.com/spreadsheets/d/"
            "test_sheet/edit"
        ),
        user_id=recruiter.id
    )

    db_setup.add(job)
    db_setup.commit()
    db_setup.refresh(job)

    def override_get_db():
        yield db_setup

    app.dependency_overrides[get_db] = override_get_db

    try:
        token = create_access_token(recruiter.id)

        with TestClient(app) as test_client:
            response = test_client.get(
                f"/jobs/{job.id}",
                headers={
                    "Authorization": f"Bearer {token}"
                }
            )

        assert response.status_code == 200
        assert response.json()["id"] == job.id

    finally:
        app.dependency_overrides.clear()



def test_expired_jwt_is_rejected(monkeypatch):
    monkeypatch.setenv(
        "JWT_SECRET_KEY",
        "test-secret-key-for-jwt-authentication"
    )

    expired_token = jwt.encode(
        {
            "sub": "test-user-id",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5)
        },
        "test-secret-key-for-jwt-authentication",
        algorithm="HS256"
    )

    with TestClient(app) as test_client:
        response = test_client.get(
            "/auth/me",
            headers={
                "Authorization": f"Bearer {expired_token}"
            }
        )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid or expired authentication token"
    )


def test_invalid_jwt_is_rejected():
    with TestClient(app) as test_client:
        response = test_client.get(
            "/auth/me",
            headers={
                "Authorization": "Bearer invalid.jwt.token"
            }
        )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid or expired authentication token"
    )
