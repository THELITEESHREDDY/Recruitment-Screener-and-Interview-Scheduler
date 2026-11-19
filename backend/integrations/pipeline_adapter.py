import hashlib
from io import BytesIO

from fastapi import UploadFile


def adapt_candidates_for_pipeline(
    candidates: list[dict]
) -> list[dict]:
    """
    Convert Google Forms candidate records into
    the recruitment pipeline's expected input.
    """

    pipeline_candidates = []

    for candidate in candidates:
        # Stable identifier for repeated imports of the same response.
        # This is a provisional deduplication key.
        identity = (
            f"{candidate['timestamp']}|"
            f"{candidate['email']}|"
            f"{candidate['resume_url']}"
        )

        candidate_id = hashlib.sha256(
            identity.encode("utf-8")
        ).hexdigest()[:36]

        pdf = UploadFile(
            filename=f"{candidate_id}.pdf",
            file=BytesIO(candidate["pdf_bytes"])
        )

        pipeline_candidates.append({
            "candidate_id": candidate_id,
            "pdf": pdf,
            "pep_score": candidate["pep_score"],
            "pep_priority": candidate["pep_priority"]
        })

    return pipeline_candidates