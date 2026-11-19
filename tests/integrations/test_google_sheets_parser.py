from backend.integrations.google_sheets import parse_candidate_responses


def test_parse_candidate_responses():
    rows = [
        [
            "Timestamp",
            "Email Address",
            "full name",
            "Email",
            "Mobile Number",
            "Resume ",
            "PEP Score",
            "PEP Priority"
        ],
        [
            "11/19/2026 15:16:47",
            "account@example.com",
            "Test Candidate",
            "candidate@example.com",
            "9876543210",
            "https://drive.google.com/open?id=example-file-id",
            "98",
            "1"
        ]
    ]

    candidates = parse_candidate_responses(rows)

    assert len(candidates) == 1

    candidate = candidates[0]

    assert candidate["full_name"] == "Test Candidate"
    assert candidate["email"] == "candidate@example.com"
    assert candidate["google_account_email"] == "account@example.com"
    assert candidate["mobile_number"] == "9876543210"
    assert candidate["pep_score"] == 98.0
    assert candidate["pep_priority"] == "1"
    assert candidate["resume_url"].startswith("https://drive.google.com/")