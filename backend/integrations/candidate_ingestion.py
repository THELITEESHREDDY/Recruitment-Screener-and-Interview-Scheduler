from backend.integrations.google_sheets import (
    get_form_responses,
    parse_candidate_responses,
)

from backend.integrations.google_drive import download_resume_pdf


def fetch_candidates(spreadsheet_id: str) -> list[dict]:
    """
    Fetch candidate information and resume PDFs
    from Google Sheets and Google Drive.
    """

    rows = get_form_responses(spreadsheet_id)

    candidates = parse_candidate_responses(rows)

    results = []

    for candidate in candidates:
        if not candidate["resume_url"]:
            continue

        pdf_bytes = download_resume_pdf(
            candidate["resume_url"]
        )

        results.append({
            **candidate,
            "pdf_bytes": pdf_bytes,
        })

    return results