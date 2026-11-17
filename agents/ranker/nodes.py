
import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from shared.llm.provider import llm_service

from sqlalchemy.exc import SQLAlchemyError

from backend.models.candidate_ranking import CandidateRanking
from .state import RankerState
from .schemas import SecondaryEvaluationOutput
from .prompts import evaluate_secondary_metrics_prompt
from .schemas import (
    SecondaryEvaluationOutput,
    SecondaryRubricOutput
)
from .prompts import (
    evaluate_secondary_metrics_prompt,
    generate_secondary_rubric_prompt
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.db.connection import LocalSession
from backend.models.job import JobDescription
from backend.models.job_ranking_rubrik import JobRankingRubric



def evaluate_secondary_metrics(state: RankerState):

    node_name = "evaluate_secondary_metrics"
    errors = list(state.get("errors", []))

    match_result = state["match_result"]
    rubric = state["secondary_rubric"]

    try:
        # Extract Matcher Agent evidence.
        matcher_evidence = {}

        for section, details in match_result["match_scores"].items():
            matcher_evidence[section] = {
                "evidence": details["evidence"],
                "justification": details["justification"],
                "matched_items": details["matched_items"],
                "missing_items": details["missing_items"]
            }

        parser = JsonOutputParser(
            pydantic_object=SecondaryEvaluationOutput
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", evaluate_secondary_metrics_prompt)
        ])

        chain = prompt | llm_service | parser

        result = chain.invoke({
            "rubric": json.dumps(rubric, indent=2),
            "matcher_evidence": json.dumps(
                matcher_evidence,
                indent=2
            ),
            "format_instructions": parser.get_format_instructions()
        })

        validated_result = SecondaryEvaluationOutput.model_validate(
            result
        )

        evaluation = validated_result.model_dump()

        # Validate criteria.
        expected_criteria = set(rubric["criteria"].keys())
        received_criteria = set(evaluation["criteria_scores"].keys())

        if expected_criteria != received_criteria:
            return {
                "errors": errors + [
                    create_agent_error(
                        node=node_name,
                        error_type="criteria_mismatch",
                        message=(
                            f"Expected {expected_criteria}, "
                            f"received {received_criteria}."
                        ),
                        retryable=True
                    )
                ]
            }

        # Validate insufficient evidence scores.
        for criterion, details in evaluation["criteria_scores"].items():

            if (
                details["evidence_status"] == "insufficient"
                and details["score"] != 50
            ):
                return {
                    "errors": errors + [
                        create_agent_error(
                            node=node_name,
                            error_type="invalid_insufficient_score",
                            message=(
                                f"Criterion '{criterion}' has insufficient "
                                f"evidence but received score "
                                f"{details['score']} instead of 50."
                            ),
                            retryable=True
                        )
                    ]
                }

        return {
            "secondary_evaluation": evaluation,
            "errors": errors
        }

    except Exception as exc:

        return {
            "errors": errors + [
                create_agent_error(
                    node=node_name,
                    error_type=type(exc).__name__,
                    message=str(exc),
                    retryable=True
                )
            ]
        }




def create_agent_error(
    node: str,
    error_type: str,
    message: str,
    retryable: bool = False
):
    return {
        "node": node,
        "error_type": error_type,
        "message": message,
        "retryable": retryable
    }



import math


def calculate_secondary_score(state: RankerState):

    node_name = "calculate_secondary_score"
    errors = list(state.get("errors", []))

    evaluation = state["secondary_evaluation"]
    rubric = state["secondary_rubric"]

    criteria_scores = evaluation["criteria_scores"]
    criteria_weights = rubric["criteria"]

    # Validate that both contain identical criteria.
    if set(criteria_scores.keys()) != set(criteria_weights.keys()):
        errors.append(
            create_agent_error(
                node=node_name,
                error_type="criteria_mismatch",
                message="Evaluation criteria do not match rubric criteria.",
                retryable=True
            )
        )

        return {"errors": errors}

    total_weight = 0.0
    weighted_sum = 0.0

    for criterion, details in criteria_scores.items():

        score = details["score"]
        weight = criteria_weights[criterion]["weight"]

        # Validate score.
        if (
            not isinstance(score, (int, float))
            or not math.isfinite(score)
            or not 0 <= score <= 100
        ):
            errors.append(
                create_agent_error(
                    node=node_name,
                    error_type="invalid_score",
                    message=f"Invalid score for criterion '{criterion}'.",
                    retryable=True
                )
            )
            continue

        # Validate weight.
        if (
            not isinstance(weight, (int, float))
            or not math.isfinite(weight)
            or weight < 0
        ):
            errors.append(
                create_agent_error(
                    node=node_name,
                    error_type="invalid_weight",
                    message=f"Invalid weight for criterion '{criterion}'.",
                    retryable=False
                )
            )
            continue

        weighted_sum += score * weight
        total_weight += weight

    # Do not calculate if any validation failed.
    if errors != state.get("errors", []):
        return {"errors": errors}

    if total_weight <= 0:
        errors.append(
            create_agent_error(
                node=node_name,
                error_type="zero_total_weight",
                message="Total rubric weight must be greater than zero.",
                retryable=False
            )
        )

        return {"errors": errors}

    secondary_score = round(
        weighted_sum / total_weight,
        2
    )

    updated_evaluation = {
        **evaluation,
        "weighted_score": secondary_score
    }

    return {
        "secondary_evaluation": updated_evaluation,
        "errors": errors
    }




def generate_secondary_rubric(state: RankerState):

    node_name = "generate_secondary_rubric"
    errors = list(state.get("errors", []))

    try:
        parser = JsonOutputParser(
            pydantic_object=SecondaryRubricOutput
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", generate_secondary_rubric_prompt)
        ])

        chain = prompt | llm_service | parser

        result = chain.invoke({
            "job_description": state["job_description"],
            "format_instructions": parser.get_format_instructions()
        })

        validated_result = SecondaryRubricOutput.model_validate(
            result
        )

        rubric = validated_result.model_dump()

        expected_criteria = {
            "relevant_experience",
            "project_impact",
            "problem_solving"
        }

        received_criteria = set(rubric["criteria"].keys())

        if expected_criteria != received_criteria:
            return {
                "errors": errors + [
                    create_agent_error(
                        node=node_name,
                        error_type="criteria_mismatch",
                        message="Generated rubric contains unexpected criteria.",
                        retryable=True
                    )
                ]
            }

        total_weight = sum(
            criterion["weight"]
            for criterion in rubric["criteria"].values()
        )

        if total_weight <= 0:
            return {
                "errors": errors + [
                    create_agent_error(
                        node=node_name,
                        error_type="invalid_total_weight",
                        message="Generated rubric has zero total weight.",
                        retryable=True
                    )
                ]
            }

        # Normalize weights to sum to 1.
        for criterion in rubric["criteria"].values():
            criterion["weight"] = criterion["weight"] / total_weight

        return {
            "secondary_rubric": rubric,
            "errors": errors
        }

    except Exception as exc:
        return {
            "errors": errors + [
                create_agent_error(
                    node=node_name,
                    error_type=type(exc).__name__,
                    message=str(exc),
                    retryable=True
                )
            ]
        }



def validate_secondary_rubric(rubric: dict) -> bool:
    expected_criteria = {
        "relevant_experience",
        "project_impact",
        "problem_solving"
    }

    if not isinstance(rubric, dict):
        return False

    criteria = rubric.get("criteria")

    if not isinstance(criteria, dict):
        return False

    if set(criteria.keys()) != expected_criteria:
        return False

    return True





def get_or_create_secondary_rubric(state: RankerState):

    node_name = "get_or_create_secondary_rubric"
    errors = list(state.get("errors", []))
    session = LocalSession()

    try:
        # Verify that the JD exists.
        job = (
            session.query(JobDescription)
            .filter(JobDescription.id == state["jd_id"])
            .first()
        )

        if job is None:
            return {
                "errors": errors + [
                    create_agent_error(
                        node=node_name,
                        error_type="job_description_not_found",
                        message=f"Job description '{state['jd_id']}' not found.",
                        retryable=False
                    )
                ]
            }

        # Retrieve an existing rubric.
        existing_rubric = (
            session.query(JobRankingRubric)
            .filter(JobRankingRubric.jd_id == state["jd_id"])
            .first()
        )

        if existing_rubric is not None:

            stored_rubric = {
                "criteria": existing_rubric.criteria
            }

            if not validate_secondary_rubric(stored_rubric):
                return {
                    "errors": errors + [
                        create_agent_error(
                            node=node_name,
                            error_type="invalid_stored_rubric",
                            message="Stored rubric contains missing or unexpected criteria.",
                            retryable=False
                        )
                    ]
                }

            return {
                "secondary_rubric": stored_rubric,
                "errors": errors
            }

        # Generate a rubric if one doesn't exist.
        # Generate a rubric if one doesn't exist.
        generation_state = {
            **state,
            "job_description": job.job_description
        }

        result = generate_secondary_rubric(generation_state)

        if result.get("errors") and len(result["errors"]) > len(errors):
            return result

        new_rubric = result["secondary_rubric"]

        if not validate_secondary_rubric(new_rubric):
            return {
                "errors": errors + [
                    create_agent_error(
                        node=node_name,
                        error_type="invalid_generated_rubric",
                        message="Generated rubric is invalid.",
                        retryable=False
                    )
                ]
            }

        # Persist the generated rubric.
        rubric_record = JobRankingRubric(
            jd_id=state["jd_id"],
            criteria=new_rubric["criteria"]
        )

        session.add(rubric_record)
        session.commit()

        return {
            "secondary_rubric": new_rubric,
            "errors": errors
        }

    except IntegrityError:

        session.rollback()

        # Another request may have created the rubric.
        existing_rubric = (
            session.query(JobRankingRubric)
            .filter(JobRankingRubric.jd_id == state["jd_id"])
            .first()
        )

        if existing_rubric is not None:

            stored_rubric = {
                "criteria": existing_rubric.criteria
            }

            if validate_secondary_rubric(stored_rubric):
                return {
                    "secondary_rubric": stored_rubric,
                    "errors": errors
                }

        return {
            "errors": errors + [
                create_agent_error(
                    node=node_name,
                    error_type="integrity_error",
                    message="Could not persist or retrieve the rubric.",
                    retryable=True
                )
            ]
        }

    except SQLAlchemyError as exc:

        session.rollback()

        return {
            "errors": errors + [
                create_agent_error(
                    node=node_name,
                    error_type="database_error",
                    message=str(exc),
                    retryable=True
                )
            ]
        }

    except Exception as exc:

        session.rollback()

        return {
            "errors": errors + [
                create_agent_error(
                    node=node_name,
                    error_type=type(exc).__name__,
                    message=str(exc),
                    retryable=False
                )
            ]
        }

    finally:
        session.close()




def rank_candidates(state: RankerState):

    candidates = list(state.get("existing_candidates", []))

    match_result = state["match_result"]
    evaluation = state["secondary_evaluation"]

    incoming_record = {
        "candidate_id": match_result["candidate_id"],
        "candidate_name": state["incoming_candidate"]["name"],
        "overall_score": match_result["overall_score"],
        "match_scores": match_result["match_scores"],
        "secondary_score": evaluation["weighted_score"],
        "secondary_details": evaluation,
        "rank": 0,
        "one_line_rationale": evaluation["overall_justification"]
    }

    existing_index = next(
        (
            index
            for index, candidate in enumerate(candidates)
            if candidate["candidate_id"] == incoming_record["candidate_id"]
        ),
        None
    )

    if existing_index is not None:
        candidates[existing_index] = incoming_record
    else:
        candidates.append(incoming_record)

    candidates.sort(
        key=lambda candidate: (
            candidate["overall_score"],
            candidate["secondary_score"]
        ),
        reverse=True
    )

    previous_scores = None
    current_rank = 0

    for index, candidate in enumerate(candidates, start=1):

        current_scores = (
            candidate["overall_score"],
            candidate["secondary_score"]
        )

        if current_scores != previous_scores:
            current_rank = index
            previous_scores = current_scores

        candidate["rank"] = current_rank

    return {
        "ranked_candidates": candidates,
        "errors": list(state.get("errors", []))
    }




def persist_rankings(state: RankerState):

    node_name = "persist_rankings"
    errors = list(state.get("errors", []))

    session = LocalSession()

    try:
        jd_id = state["jd_id"]
        ranked_candidates = state["ranked_candidates"]

        # Retrieve existing rankings for this JD.
        existing_records = {
            record.candidate_id: record
            for record in (
                session.query(CandidateRanking)
                .filter(CandidateRanking.jd_id == jd_id)
                .all()
            )
        }

        for candidate in ranked_candidates:

            candidate_id = candidate["candidate_id"]

            record = existing_records.get(candidate_id)

            if record is None:
                record = CandidateRanking(
                    jd_id=jd_id,
                    candidate_id=candidate_id
                )
                session.add(record)

            # Insert or update ranking data.
            record.overall_score = candidate["overall_score"]
            record.match_scores = candidate["match_scores"]
            record.secondary_score = candidate["secondary_score"]
            record.secondary_details = candidate["secondary_details"]
            record.rank = candidate["rank"]
            record.one_line_rationale = candidate["one_line_rationale"]

        session.commit()

        return {
            "errors": errors
        }

    except SQLAlchemyError as exc:

        session.rollback()

        errors.append(
            create_agent_error(
                node=node_name,
                error_type="database_error",
                message=str(exc),
                retryable=True
            )
        )

        return {
            "errors": errors
        }

    except Exception as exc:

        session.rollback()

        errors.append(
            create_agent_error(
                node=node_name,
                error_type=type(exc).__name__,
                message=str(exc),
                retryable=False
            )
        )

        return {
            "errors": errors
        }

    finally:
        session.close()



def load_existing_rankings(state: RankerState):
    node_name = "load_existing_rankings"
    errors = list(state.get("errors", []))
    session = LocalSession()

    try:
        records = (
            session.query(CandidateRanking)
            .filter(CandidateRanking.jd_id == state["jd_id"])
            .order_by(CandidateRanking.rank.asc())
            .all()
        )

        existing_candidates = [
            {
                "candidate_id": record.candidate_id,
                "candidate_name": record.candidate.name,
                "overall_score": record.overall_score,
                "match_scores": record.match_scores,
                "secondary_score": record.secondary_score,
                "secondary_details": record.secondary_details,
                "rank": record.rank,
                "one_line_rationale": record.one_line_rationale
            }
            for record in records
        ]

        return {
            "existing_candidates": existing_candidates,
            "errors": errors
        }

    except SQLAlchemyError as exc:
        session.rollback()

        errors.append(
            create_agent_error(
                node=node_name,
                error_type="database_error",
                message=str(exc),
                retryable=True
            )
        )

        return {"errors": errors}

    except Exception as exc:
        session.rollback()

        errors.append(
            create_agent_error(
                node=node_name,
                error_type=type(exc).__name__,
                message=str(exc),
                retryable=False
            )
        )

        return {"errors": errors}

    finally:
        session.close()
