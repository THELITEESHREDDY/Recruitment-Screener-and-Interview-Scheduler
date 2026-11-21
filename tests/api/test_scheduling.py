from fastapi.testclient import TestClient
import pytest
from backend.main import app
from backend.db.connection import get_db
from backend.models.job import JobDescription
from backend.models.candidate import Candidate
from backend.models.candidate_ranking import CandidateRanking


def test_schedule_interviews(db_setup):

    app.dependency_overrides[get_db] = lambda: db_setup

    try:
        # Create a test job.
        job = JobDescription(
            job_description="Python Backend Engineer"
        )

        db_setup.add(job)
        db_setup.flush()

        # Create two mock candidates.
        candidates = [
            Candidate(
                id="CAND_001",
                name="Alice",
                email="alice@example.com",
                mobile_number="9876543210",
                google_form_response_id="FORM_001"
            ),
            Candidate(
                id="CAND_002",
                name="Bob",
                email="bob@example.com",
                mobile_number="9876543211",
                google_form_response_id="FORM_002"
            )
        ]

        db_setup.add_all(candidates)
        db_setup.flush()

        # Create rankings for the job.
        rankings = [
            CandidateRanking(
                jd_id=job.id,
                candidate_id="CAND_001",
                overall_score=95,
                secondary_score=85,
                match_scores={},
                secondary_details={},
                rank=1,
                one_line_rationale="Strong match"
            ),
            CandidateRanking(
                jd_id=job.id,
                candidate_id="CAND_002",
                overall_score=88,
                secondary_score=80,
                match_scores={},
                secondary_details={},
                rank=2,
                one_line_rationale="Good match"
            )
        ]

        db_setup.add_all(rankings)
        db_setup.commit()

        client = TestClient(app)

        response = client.post(
            f"/jobs/{job.id}/schedule",
            json={
                "mode": "automatic",
                "top_n": 2,
                "interview_duration_minutes": 30,
                "start_date": "2026-11-23",
                "daily_working_hours": {
                    "start_time": "10:00",
                    "end_time": "11:00"
                }
            }
        )

        assert response.status_code == 200, response.text

        data = response.json()

        assert data["total_scheduled"] == 2
        assert data["mode"] == "automatic"

        assert [
            item["candidate_id"]
            for item in data["schedule"]
        ] == ["CAND_001", "CAND_002"]

        assert data["schedule"][0]["interview_slot"] == {
            "date": "2026-11-23",
            "start_time": "10:00",
            "end_time": "10:30"
        }

        assert data["schedule"][1]["interview_slot"] == {
            "date": "2026-11-23",
            "start_time": "10:30",
            "end_time": "11:00"
        }

    finally:
        app.dependency_overrides.clear()


def test_explicit_scheduling_api(db_setup):

    app.dependency_overrides[get_db] = lambda: db_setup

    try:
        job = JobDescription(
            job_description="Backend Developer"
        )

        db_setup.add(job)
        db_setup.flush()

        for i, name in enumerate(["Alice", "Bob"], start=1):
            candidate_id = f"CAND_00{i}"

            db_setup.add(
                Candidate(
                    id=candidate_id,
                    name=name,
                    email=f"candidate{i}@example.com",
                    mobile_number=f"987654321{i}",
                    google_form_response_id=f"FORM_00{i}"
                )
            )

            db_setup.add(
                CandidateRanking(
                    jd_id=job.id,
                    candidate_id=candidate_id,
                    overall_score=100 - i * 5,
                    secondary_score=80,
                    match_scores={},
                    secondary_details={},
                    rank=i,
                    one_line_rationale="Test ranking"
                )
            )

        db_setup.commit()

        client = TestClient(app)

        response = client.post(
            f"/jobs/{job.id}/schedule",
            json={
                "mode": "explicit",
                "top_n": 2,
                "interview_duration_minutes": 30,
                "schedule": [
                    {
                        "date": "2026-11-24",
                        "start_time": "14:00",
                        "end_time": "14:30"
                    },
                    {
                        "date": "2026-11-23",
                        "start_time": "10:00",
                        "end_time": "10:30"
                    }
                ]
            }
        )

        assert response.status_code == 200, response.text

        data = response.json()

        assert data["mode"] == "explicit"
        assert data["total_scheduled"] == 2

        assert [
            item["candidate_id"]
            for item in data["schedule"]
        ] == ["CAND_001", "CAND_002"]

        # Slots must be assigned chronologically.
        assert data["schedule"][0]["interview_slot"] == {
            "date": "2026-11-23",
            "start_time": "10:00",
            "end_time": "10:30"
        }

        assert data["schedule"][1]["interview_slot"] == {
            "date": "2026-11-24",
            "start_time": "14:00",
            "end_time": "14:30"
        }

    finally:
        app.dependency_overrides.clear()




@pytest.mark.parametrize(
    "payload",
    [
        # Invalid top_n
        {
            "mode": "automatic",
            "top_n": 0,
            "interview_duration_minutes": 30,
            "start_date": "2026-11-23",
            "daily_working_hours": {
                "start_time": "10:00",
                "end_time": "12:00"
            }
        },

        # Missing schedule in explicit mode
        {
            "mode": "explicit",
            "top_n": 2,
            "interview_duration_minutes": 30
        },

        # Missing working hours in automatic mode
        {
            "mode": "automatic",
            "top_n": 2,
            "interview_duration_minutes": 30,
            "start_date": "2026-11-23"
        },

        # Unsupported scheduling mode
        {
            "mode": "random",
            "top_n": 2,
            "interview_duration_minutes": 30
        },

        # Invalid interview duration
        {
            "mode": "automatic",
            "top_n": 2,
            "interview_duration_minutes": 0,
            "start_date": "2026-11-23",
            "daily_working_hours": {
                "start_time": "10:00",
                "end_time": "12:00"
            }
        }
    ]
)
def test_invalid_scheduling_requests(payload):
    client = TestClient(app)

    response = client.post(
        "/jobs/test-job-id/schedule",
        json=payload
    )

    assert response.status_code == 422



def test_schedule_job_not_found(db_setup):
    app.dependency_overrides[get_db] = lambda: db_setup

    try:
        client = TestClient(app)

        response = client.post(
            "/jobs/nonexistent-job/schedule",
            json={
                "mode": "automatic",
                "top_n": 1,
                "interview_duration_minutes": 30,
                "start_date": "2026-11-23",
                "daily_working_hours": {
                    "start_time": "10:00",
                    "end_time": "12:00"
                }
            }
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Job not found"

    finally:
        app.dependency_overrides.clear()


def test_schedule_no_ranked_candidates(db_setup):
    app.dependency_overrides[get_db] = lambda: db_setup

    try:
        job = JobDescription(
            job_description="Python Backend Engineer"
        )

        db_setup.add(job)
        db_setup.commit()

        client = TestClient(app)

        response = client.post(
            f"/jobs/{job.id}/schedule",
            json={
                "mode": "automatic",
                "top_n": 1,
                "interview_duration_minutes": 30,
                "start_date": "2026-11-23",
                "daily_working_hours": {
                    "start_time": "10:00",
                    "end_time": "12:00"
                }
            }
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "No ranked candidates available"
        )

    finally:
        app.dependency_overrides.clear()

def test_schedule_insufficient_slots(db_setup):
    app.dependency_overrides[get_db] = lambda: db_setup

    try:
        job = JobDescription(
            job_description="Backend Engineer"
        )
        db_setup.add(job)
        db_setup.flush()

        for i in range(1, 4):
            candidate_id = f"CAND_00{i}"

            db_setup.add(
                Candidate(
                    id=candidate_id,
                    name=f"Candidate {i}",
                    email=f"candidate{i}@example.com",
                    mobile_number=f"987654321{i}",
                    google_form_response_id=f"FORM_00{i}"
                )
            )

            db_setup.add(
                CandidateRanking(
                    jd_id=job.id,
                    candidate_id=candidate_id,
                    overall_score=100 - i * 5,
                    secondary_score=80,
                    match_scores={},
                    secondary_details={},
                    rank=i,
                    one_line_rationale="Test ranking"
                )
            )

        db_setup.commit()

        client = TestClient(app)

        response = client.post(
            f"/jobs/{job.id}/schedule",
            json={
                "mode": "explicit",
                "top_n": 3,
                "interview_duration_minutes": 30,
                "schedule": [
                    {
                        "date": "2026-11-23",
                        "start_time": "10:00",
                        "end_time": "11:00"
                    }
                ]
            }
        )

        assert response.status_code == 422
        assert "Insufficient interview slots" in (
            response.json()["detail"]
        )

    finally:
        app.dependency_overrides.clear()


def test_schedule_insufficient_candidates(db_setup):
    app.dependency_overrides[get_db] = lambda: db_setup

    try:
        job = JobDescription(
            job_description="Python Developer"
        )

        db_setup.add(job)
        db_setup.flush()

        candidate = Candidate(
            id="CAND_001",
            name="Alice",
            email="alice@example.com",
            mobile_number="9876543210",
            google_form_response_id="FORM_001"
        )

        db_setup.add(candidate)
        db_setup.flush()

        db_setup.add(
            CandidateRanking(
                jd_id=job.id,
                candidate_id=candidate.id,
                overall_score=95,
                secondary_score=85,
                match_scores={},
                secondary_details={},
                rank=1,
                one_line_rationale="Strong candidate"
            )
        )

        db_setup.commit()

        client = TestClient(app)

        response = client.post(
            f"/jobs/{job.id}/schedule",
            json={
                "mode": "automatic",
                "top_n": 3,
                "interview_duration_minutes": 30,
                "start_date": "2026-11-23",
                "daily_working_hours": {
                    "start_time": "10:00",
                    "end_time": "12:00"
                }
            }
        )

        assert response.status_code == 422
        assert "Not enough ranked candidates" in (
            response.json()["detail"]
        )

    finally:
        app.dependency_overrides.clear()