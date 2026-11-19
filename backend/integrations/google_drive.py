from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


BASE_DIR = Path(__file__).resolve().parents[2]

CREDENTIALS_FILE = (
    BASE_DIR / "credentials" / "google-service-account.json"
)

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly"
]


def get_drive_service():
    """
    Authenticate with Google Drive using the service account.
    """

    credentials = service_account.Credentials.from_service_account_file(
        str(CREDENTIALS_FILE),
        scopes=SCOPES
    )

    return build(
        "drive",
        "v3",
        credentials=credentials
    )


def extract_drive_file_id(resume_url: str) -> str:
    """
    Extract file ID from Google Drive URLs.
    Supports:
      - https://drive.google.com/open?id=FILE_ID
      - https://drive.google.com/file/d/FILE_ID/view
    """

    parsed = urlparse(resume_url)

    if parsed.hostname not in ("drive.google.com", "www.drive.google.com"):
        raise ValueError("Invalid Google Drive URL")

    query_id = parse_qs(parsed.query).get("id")

    if query_id:
        return query_id[0]

    parts = parsed.path.strip("/").split("/")

    if len(parts) >= 3 and parts[0] == "file" and parts[1] == "d":
        return parts[2]

    raise ValueError("Could not extract Google Drive file ID")


def download_resume_pdf(resume_url: str) -> bytes:
    """
    Download a candidate's PDF resume from Google Drive.
    """

    file_id = extract_drive_file_id(resume_url)

    service = get_drive_service()

    metadata = service.files().get(
        fileId=file_id,
        fields="id,name,mimeType,size"
    ).execute()

    if metadata.get("mimeType") != "application/pdf":
        raise ValueError("Resume must be a PDF file")

    request = service.files().get_media(fileId=file_id)

    buffer = BytesIO()

    downloader = MediaIoBaseDownload(
        buffer,
        request
    )

    done = False

    while not done:
        _, done = downloader.next_chunk()

    pdf_bytes = buffer.getvalue()

    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("Downloaded file is not a valid PDF")

    return pdf_bytes