import os

from backend.integrations.google_drive import (
    extract_drive_file_id,
    download_resume_pdf
)


def test_extract_drive_file_id():
    url = "https://drive.google.com/open?id=187sWB9kwAwRjBFAnJ3C-ihDoJdbZ7Bxe"

    file_id = extract_drive_file_id(url)

    assert file_id == "187sWB9kwAwRjBFAnJ3C-ihDoJdbZ7Bxe"


def test_download_resume_pdf():
    resume_url = os.environ["TEST_RESUME_URL"]

    pdf_bytes = download_resume_pdf(resume_url)

    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 0

    print(f"\nDownloaded resume: {len(pdf_bytes)} bytes")