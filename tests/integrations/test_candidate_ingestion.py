from backend.integrations import candidate_ingestion


def test_fetch_candidates(monkeypatch):
    rows = [
        [
            "Timestamp", "Email Address", "full name",
            "Email", "Mobile Number", "Resume ",
            "PEP Score", "PEP Priority"
        ],
        [
            "11/19/2026 15:16:47",
            "account@example.com",
            "Test Candidate",
            "candidate@example.com",
            "9876543210",
            "https://drive.google.com/open?id=test-file-id",
            "98",
            "1"
        ]
    ]

    monkeypatch.setattr(
        candidate_ingestion,
        "get_form_responses",
        lambda spreadsheet_id: rows
    )

    monkeypatch.setattr(
        candidate_ingestion,
        "download_resume_pdf",
        lambda url: b"%PDF-1.4 test content"
    )

    result = candidate_ingestion.fetch_candidates(
        "test-spreadsheet-id"
    )

    assert len(result) == 1
    assert result[0]["full_name"] == "Test Candidate"
    assert result[0]["pep_score"] == 98.0
    assert result[0]["pdf_bytes"].startswith(b"%PDF-")