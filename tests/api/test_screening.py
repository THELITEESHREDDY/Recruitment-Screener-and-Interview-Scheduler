from fastapi.testclient import TestClient
from backend.main import app
from backend.db.connection import get_db
from backend.models.job import JobDescription
from backend.api import screening


def test_screen_candidates(db_setup, monkeypatch):
    # Use isolated test database
    app.dependency_overrides[get_db] = lambda: db_setup

    job = JobDescription(
        job_description="Python Backend Engineer"
    )

    db_setup.add(job)
    db_setup.commit()
    db_setup.refresh(job)

    # Mock Google Sheets + Drive
    monkeypatch.setattr(
        screening,
        "fetch_candidates",
        lambda spreadsheet_id: [
            {
                "email": "test@example.com",
                "pdf_bytes": b"%PDF-1.4",
            }
        ]
    )

    # Mock adapter
    monkeypatch.setattr(
        screening,
        "adapt_candidates_for_pipeline",
        lambda candidates: [
            {
                "candidate_id": "CAND_001",
                "pdf": None,
                "pep_score": 98,
                "pep_priority": "1",
            }
        ]
    )

    # Mock recruitment pipeline
    async def mock_pipeline(**kwargs):
        return {
            "ranked_candidates": [],
            "schedule": [],
            "candidate_errors": [],
            "scheduler_errors": [],
        }

    monkeypatch.setattr(
        screening,
        "run_recruitment_pipeline",
        mock_pipeline
    )

    monkeypatch.setenv(
        "GOOGLE_SPREADSHEET_ID",
        "test-spreadsheet-id"
    )

    try:
        client = TestClient(app)

        response = client.post(
            f"/jobs/{job.id}/screen?top_n=1"
        )

        assert response.status_code == 200

        data = response.json()

        assert "ranked_candidates" in data
        assert "schedule" in data
        assert "candidate_errors" in data
        assert "scheduler_errors" in data

    finally:
        app.dependency_overrides.clear()


def test_screen_skips_already_ranked_candidates(
    db_setup,
    monkeypatch
):
    from backend.models.candidate import Candidate
    from backend.models.candidate_ranking import CandidateRanking

    app.dependency_overrides[get_db] = lambda: db_setup

    job = JobDescription(
        job_description="Python Backend Engineer"
    )

    candidate = Candidate(
        id="CAND_001",
        name="Test Candidate",
        email="test@example.com",
        mobile_number="9876543210",
        linkedin_url=None,
        google_form_response_id="FORM_001"
    )

    db_setup.add_all([job, candidate])
    db_setup.flush()

    ranking = CandidateRanking(
        jd_id=job.id,
        candidate_id=candidate.id,
        overall_score=85.0,
        secondary_score=75.0,
        match_scores={},
        secondary_details={},
        rank=1,
        one_line_rationale="Existing ranking"
    )

    db_setup.add(ranking)
    db_setup.commit()

    monkeypatch.setenv(
        "GOOGLE_SPREADSHEET_ID",
        "test-spreadsheet-id"
    )

    monkeypatch.setattr(
        screening,
        "fetch_candidates",
        lambda spreadsheet_id: [{"resume_url": "mock"}]
    )

    monkeypatch.setattr(
        screening,
        "adapt_candidates_for_pipeline",
        lambda candidates: [
            {"candidate_id": "CAND_001"}
        ]
    )

    async def mock_pipeline(**kwargs):
        raise AssertionError(
            "Pipeline should not run for an already ranked candidate"
        )

    monkeypatch.setattr(
        screening,
        "run_recruitment_pipeline",
        mock_pipeline
    )

    try:
        client = TestClient(app)

        response = client.post(
            f"/jobs/{job.id}/screen?top_n=1"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["new_candidates"] == 0
        assert data["message"] == (
            "All candidates have already been screened for this job"
        )

    finally:
        app.dependency_overrides.clear()



def test_screen_processes_only_new_candidates(
    db_setup,
    monkeypatch
):
    from backend.models.candidate import Candidate
    from backend.models.candidate_ranking import CandidateRanking

    app.dependency_overrides[get_db] = lambda: db_setup

    job = JobDescription(
        job_description="Python Backend Engineer"
    )

    existing_candidate = Candidate(
        id="CAND_001",
        name="Existing Candidate",
        email="existing@example.com",
        mobile_number="9876543210",
        linkedin_url=None,
        google_form_response_id="FORM_001"
    )

    db_setup.add_all([job, existing_candidate])
    db_setup.flush()

    existing_ranking = CandidateRanking(
        jd_id=job.id,
        candidate_id=existing_candidate.id,
        overall_score=85.0,
        secondary_score=75.0,
        match_scores={},
        secondary_details={},
        rank=1,
        one_line_rationale="Already screened"
    )

    db_setup.add(existing_ranking)
    db_setup.commit()

    monkeypatch.setenv(
        "GOOGLE_SPREADSHEET_ID",
        "test-spreadsheet-id"
    )

    # Google Forms contains an existing and a new candidate.
    monkeypatch.setattr(
        screening,
        "fetch_candidates",
        lambda spreadsheet_id: [
            {"email": "existing@example.com"},
            {"email": "new@example.com"}
        ]
    )

    monkeypatch.setattr(
        screening,
        "adapt_candidates_for_pipeline",
        lambda candidates: [
            {"candidate_id": "CAND_001"},
            {"candidate_id": "CAND_002"}
        ]
    )

    pipeline_calls = []

    async def mock_pipeline(**kwargs):
        pipeline_calls.append(kwargs)

        return {
            "ranked_candidates": [
                {"candidate_id": "CAND_002", "rank": 1}
            ],
            "schedule": [],
            "candidate_errors": [],
            "scheduler_errors": []
        }

    monkeypatch.setattr(
        screening,
        "run_recruitment_pipeline",
        mock_pipeline
    )

    try:
        client = TestClient(app)

        response = client.post(
            f"/jobs/{job.id}/screen?top_n=1"
        )

        assert response.status_code == 200

        # Pipeline must run exactly once.
        assert len(pipeline_calls) == 1

        # Only the new candidate should enter the pipeline.
        processed_candidates = pipeline_calls[0]["candidates"]

        assert len(processed_candidates) == 1
        assert processed_candidates[0]["candidate_id"] == "CAND_002"

        assert pipeline_calls[0]["jd_id"] == job.id
        assert pipeline_calls[0]["top_n"] == 1

        assert response.json()["ranked_candidates"][0]["candidate_id"] == "CAND_002"

    finally:
        app.dependency_overrides.clear()


def test_screen_processes_only_new_candidates(
    db_setup,
    monkeypatch
):
    from backend.models.candidate import Candidate
    from backend.models.candidate_ranking import CandidateRanking

    app.dependency_overrides[get_db] = lambda: db_setup

    job = JobDescription(
        job_description="Python Backend Engineer"
    )

    existing_candidate = Candidate(
        id="CAND_001",
        name="Existing Candidate",
        email="existing@example.com",
        mobile_number="9876543210",
        linkedin_url=None,
        google_form_response_id="FORM_001"
    )

    db_setup.add_all([job, existing_candidate])
    db_setup.flush()

    existing_ranking = CandidateRanking(
        jd_id=job.id,
        candidate_id=existing_candidate.id,
        overall_score=85.0,
        secondary_score=75.0,
        match_scores={},
        secondary_details={},
        rank=1,
        one_line_rationale="Already screened"
    )

    db_setup.add(existing_ranking)
    db_setup.commit()

    monkeypatch.setenv(
        "GOOGLE_SPREADSHEET_ID",
        "test-spreadsheet-id"
    )

    # Google Forms contains an existing and a new candidate.
    monkeypatch.setattr(
        screening,
        "fetch_candidates",
        lambda spreadsheet_id: [
            {"email": "existing@example.com"},
            {"email": "new@example.com"}
        ]
    )

    monkeypatch.setattr(
        screening,
        "adapt_candidates_for_pipeline",
        lambda candidates: [
            {"candidate_id": "CAND_001"},
            {"candidate_id": "CAND_002"}
        ]
    )

    pipeline_calls = []

    async def mock_pipeline(**kwargs):
        pipeline_calls.append(kwargs)

        return {
            "ranked_candidates": [
                {"candidate_id": "CAND_002", "rank": 1}
            ],
            "schedule": [],
            "candidate_errors": [],
            "scheduler_errors": []
        }

    monkeypatch.setattr(
        screening,
        "run_recruitment_pipeline",
        mock_pipeline
    )

    try:
        client = TestClient(app)

        response = client.post(
            f"/jobs/{job.id}/screen?top_n=1"
        )

        assert response.status_code == 200

        # Pipeline must run exactly once.
        assert len(pipeline_calls) == 1

        # Only the new candidate should enter the pipeline.
        processed_candidates = pipeline_calls[0]["candidates"]

        assert len(processed_candidates) == 1
        assert processed_candidates[0]["candidate_id"] == "CAND_002"

        assert pipeline_calls[0]["jd_id"] == job.id
        assert pipeline_calls[0]["top_n"] == 1

        assert response.json()["ranked_candidates"][0]["candidate_id"] == "CAND_002"

    finally:
        app.dependency_overrides.clear()