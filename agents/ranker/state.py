from typing import TypedDict,NotRequired
from agents.matcher.state.candidate import CandidateState
from agents.matcher.state.match_result import MatchResult



class SecondaryCriterion(TypedDict):
    weight: float
    description: str
    evaluation_guidelines: list[str]

class SecondaryRubric(TypedDict):
    criteria: dict[str, SecondaryCriterion]

class CriterionEvaluationState(TypedDict):
    score: float
    evidence_status: str
    justification: str

class AgentError(TypedDict):
    node: str
    error_type: str
    message: str
    retryable: bool

class SecondaryEvaluation(TypedDict):
    criteria_scores: dict[str, CriterionEvaluationState]
    overall_justification: str
    weighted_score: NotRequired[float]

class RankedCandidate(TypedDict):
    candidate_id: str
    candidate_name: str
    overall_score: float
    match_scores: dict
    secondary_score: float
    secondary_details: SecondaryEvaluation
    rank: int
    one_line_rationale: str

class RankerState(TypedDict):
    jd_id: str
    job_description: str

    incoming_candidate: CandidateState
    match_result: MatchResult

    existing_candidates: list[RankedCandidate]

    secondary_rubric: SecondaryRubric
    secondary_evaluation: SecondaryEvaluation

    ranked_candidates: list[RankedCandidate]
    errors: NotRequired[list[AgentError]]