from backend.integrations.pipeline_adapter import (
    adapt_candidates_for_pipeline
)


def test_adapt_candidates_for_pipeline():
    candidates = [
        {
            "timestamp": "11/19/2026 15:16:47",
            "email": "candidate@example.com",
            "resume_url": "https://drive.google.com/open?id=test-file-id",
            "pdf_bytes": b"%PDF-1.4 test content",
            "pep_score": 98.0,
            "pep_priority": "1"
        }
    ]

    result = adapt_candidates_for_pipeline(candidates)

    assert len(result) == 1

    candidate = result[0]

    assert isinstance(candidate["candidate_id"], str)
    assert len(candidate["candidate_id"]) == 36

    assert candidate["pdf"].filename.endswith(".pdf")
    assert candidate["pdf"].file.read().startswith(b"%PDF-")

    assert candidate["pep_score"] == 98.0
    assert candidate["pep_priority"] == "1"

    # Repeated imports must generate the same candidate ID.
    repeated = adapt_candidates_for_pipeline(candidates)

    assert (
        candidate["candidate_id"]
        == repeated[0]["candidate_id"]
    )