import os

from backend.integrations.google_sheets import get_form_responses


def test_google_sheets_connection():
    spreadsheet_id = os.environ["GOOGLE_SPREADSHEET_ID"]

    responses = get_form_responses(spreadsheet_id)

    print("\nGoogle Sheets Responses:")
    for row in responses:
        print(row)

    assert len(responses) > 0



def parse_candidate_responses(rows: list[list[str]]) -> list[dict]:
    """
    Convert Google Sheets rows into structured candidate records.
    """

    if not rows:
        return []

    headers = [
        header.strip().lower()
        for header in rows[0]
    ]

    candidates = []

    for row in rows[1:]:
        if not any(str(value).strip() for value in row):
            continue

        # Handle missing optional cells.
        padded_row = row + [""] * (len(headers) - len(row))

        response = dict(zip(headers, padded_row))

        pep_score_raw = response.get("pep score", "").strip()

        candidate = {
            "timestamp": response.get("timestamp", ""),
            "google_account_email": response.get("email address", ""),
            "full_name": response.get("full name", ""),
            "email": response.get("email", ""),
            "mobile_number": response.get("mobile number", ""),
            "resume_url": response.get("resume", ""),
            "pep_score": (
                float(pep_score_raw)
                if pep_score_raw
                else None
            ),
            "pep_priority": response.get("pep priority", "")
        }

        candidates.append(candidate)

    return candidates