from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build


BASE_DIR = Path(__file__).resolve().parents[2]

CREDENTIALS_FILE = (
    BASE_DIR / "credentials" / "google-service-account.json"
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]


def get_sheets_service():
    """
    Authenticate using the Google service account.
    """

    credentials = service_account.Credentials.from_service_account_file(
        str(CREDENTIALS_FILE),
        scopes=SCOPES
    )

    service = build(
        "sheets",
        "v4",
        credentials=credentials
    )

    return service


def get_form_responses(
    spreadsheet_id: str,
    sheet_range: str = "'Form Responses 1'!A:Z"
):
    """
    Retrieve candidate responses from Google Sheets.
    """

    service = get_sheets_service()

    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=spreadsheet_id,
            range=sheet_range
        )
        .execute()
    )

    return result.get("values", [])



def parse_candidate_responses(rows: list[list[str]]) -> list[dict]:
    """
    Convert raw Google Sheets rows into candidate dictionaries.
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