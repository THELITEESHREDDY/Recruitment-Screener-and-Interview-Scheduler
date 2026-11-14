from typing import TypedDict, NotRequired

from .candidate import CandidateState
from .ideal_candidate import IdealCandidate
from .match_result import MatchResult


class MatcherState(TypedDict):
    jd_id: str
    job_description: str

    candidate: CandidateState
    ideal_candidate: NotRequired[IdealCandidate | None]

    match_result: NotRequired[MatchResult]

    retry_count: int
    validation_errors: list[str]