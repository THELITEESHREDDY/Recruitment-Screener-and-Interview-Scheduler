from fastapi.testclient import TestClient
from backend.main import app
from backend.db.connection import get_db
from backend.models.job import JobDescription
from backend.api import screening
from backend.models.candidate import Candidate
from backend.models.candidate_ranking import CandidateRanking

def test_screen_candidates(db_setup, monkeypatch):
    # Use isolated test database
    app.dependency_overrides[get_db] = lambda: db_setup

    job = JobDescription(
        job_description="Python Backend Engineer",
        spreadsheet_url=(
            "https://docs.google.com/spreadsheets/"
            "d/TEST_SPREADSHEET_001/edit"
        )
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
            "candidate_errors": [],
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

        data = response.json()

        assert "ranked_candidates" in data
        assert "schedule" not in data
        assert "candidate_errors" in data
        assert "scheduler_errors" not in data

    finally:
        app.dependency_overrides.clear()


def test_screen_skips_already_ranked_candidates(
    db_setup,
    monkeypatch
):
    

    app.dependency_overrides[get_db] = lambda: db_setup

    job = JobDescription(
        job_description="Python Backend Engineer",
        spreadsheet_url=(
            "https://docs.google.com/spreadsheets/"
            "d/TEST_SPREADSHEET_001/edit"
        )
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
    

    app.dependency_overrides[get_db] = lambda: db_setup

    job = JobDescription(
        job_description="Python Backend Engineer",
        spreadsheet_url=(
            "https://docs.google.com/spreadsheets/"
            "d/TEST_SPREADSHEET_001/edit"
        )
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
    

    app.dependency_overrides[get_db] = lambda: db_setup

    job = JobDescription(
        job_description="Python Backend Engineer",
        spreadsheet_url=(
            "https://docs.google.com/spreadsheets/"
            "d/TEST_SPREADSHEET_001/edit"
        )
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
                {
                    "candidate_id": "CAND_002",
                    "candidate_name": "New Candidate",
                    "rank": 1,
                    "overall_score": 90.0
                }
            ],
            "candidate_errors": []
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

def test_each_job_uses_its_own_spreadsheet(
    db_setup,
    monkeypatch
):
    app.dependency_overrides[get_db] = lambda: db_setup

    job_a = JobDescription(
        job_description="Python Backend Engineer",
        spreadsheet_url=(
            "https://docs.google.com/spreadsheets/d/SHEET_A/edit"
        )
    )

    job_b = JobDescription(
        job_description="Frontend Engineer",
        spreadsheet_url=(
            "https://docs.google.com/spreadsheets/d/SHEET_B/edit"
        )
    )

    db_setup.add_all([job_a, job_b])
    db_setup.commit()

    fetched_spreadsheets = []

    def mock_fetch_candidates(spreadsheet_id):
        fetched_spreadsheets.append(spreadsheet_id)

        return [
            {
                "candidate_id": f"CAND_{spreadsheet_id}"
            }
        ]

    monkeypatch.setattr(
        screening,
        "fetch_candidates",
        mock_fetch_candidates
    )

    monkeypatch.setattr(
        screening,
        "adapt_candidates_for_pipeline",
        lambda candidates: candidates
    )

    async def mock_pipeline(**kwargs):
        return {
            "ranked_candidates": [],
            "candidate_errors": []
        }

    monkeypatch.setattr(
        screening,
        "run_recruitment_pipeline",
        mock_pipeline
    )

    try:
        client = TestClient(app)

        response_a = client.post(
            f"/jobs/{job_a.id}/screen"
        )

        response_b = client.post(
            f"/jobs/{job_b.id}/screen"
        )

        assert response_a.status_code == 200
        assert response_b.status_code == 200

        assert fetched_spreadsheets == [
            "SHEET_A",
            "SHEET_B"
        ]

    finally:
        app.dependency_overrides.clear()


def test_screen_multiple_candidates(
    db_setup,
    monkeypatch
):
    app.dependency_overrides[get_db] = lambda: db_setup

    job = JobDescription(
        job_description="Python Backend Engineer",
        spreadsheet_url=(
            "https://docs.google.com/spreadsheets/d/TEST_SHEET/edit"
        )
    )

    db_setup.add(job)
    db_setup.commit()
    db_setup.refresh(job)

    # Simulate three candidates fetched from Google Sheets.
    mock_candidates = [
        {"candidate_id": "CAND_001"},
        {"candidate_id": "CAND_002"},
        {"candidate_id": "CAND_003"},
    ]

    fetched_ids = []
    pipeline_inputs = []

    def mock_fetch_candidates(spreadsheet_id):
        fetched_ids.append(spreadsheet_id)
        return mock_candidates

    monkeypatch.setattr(
        screening,
        "fetch_candidates",
        mock_fetch_candidates
    )

    monkeypatch.setattr(
        screening,
        "adapt_candidates_for_pipeline",
        lambda candidates: candidates
    )

    async def mock_pipeline(**kwargs):
        pipeline_inputs.extend(kwargs["candidates"])

        return {
            "ranked_candidates": [
                {
                    "candidate_id": candidate["candidate_id"],
                    "rank": index,
                    "overall_score": 90 - index
                }
                for index, candidate in enumerate(
                    kwargs["candidates"],
                    start=1
                )
            ],
            "candidate_errors": []
        }

    monkeypatch.setattr(
        screening,
        "run_recruitment_pipeline",
        mock_pipeline
    )

    try:
        client = TestClient(app)

        response = client.post(
            f"/jobs/{job.id}/screen"
        )

        assert response.status_code == 200

        assert fetched_ids == ["TEST_SHEET"]

        assert len(pipeline_inputs) == 3

        assert {
            candidate["candidate_id"]
            for candidate in pipeline_inputs
        } == {
            "CAND_001",
            "CAND_002",
            "CAND_003"
        }

        data = response.json()

        assert len(data["ranked_candidates"]) == 3
        assert data["candidate_errors"] == []

    finally:
        app.dependency_overrides.clear()