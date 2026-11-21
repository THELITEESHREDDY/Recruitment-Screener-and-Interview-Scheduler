from urllib.parse import urlparse


def extract_spreadsheet_id(url: str) -> str:
    parsed = urlparse(url.strip())

    if parsed.scheme != "https":
        raise ValueError("Google Sheets URL must use HTTPS")

    if parsed.hostname != "docs.google.com":
        raise ValueError("Invalid Google Sheets URL")

    parts = parsed.path.strip("/").split("/")

    if (
        len(parts) < 3
        or parts[0] != "spreadsheets"
        or parts[1] != "d"
        or not parts[2]
    ):
        raise ValueError("Invalid Google Sheets URL format")

    return parts[2]