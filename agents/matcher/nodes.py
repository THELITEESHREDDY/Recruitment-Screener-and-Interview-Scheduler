from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
from shared.llm.provider import llm_service
from .state.matcher_state import MatcherState
from .prompts import match_candidate_prompt,generate_ideal_candidate_prompt
from .schemas import MatchScores, IdealCandidate
import math
from agents.db.connection import LocalSession
from agents.db.models import IdealCandidateModel



MAX_RETRIES = 2

def match_candidate(state: MatcherState):
    """
    Evaluate candidate profile against the ideal candidate.
    """

    candidate = state["candidate"]
    ideal_candidate = state["ideal_candidate"]

    parser = JsonOutputParser(
        pydantic_object=MatchScores
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", match_candidate_prompt),
        ("user", """
        Ideal Candidate: {ideal_candidate}

        Candidate Profile: {candidate}
        """)
    ])

    chain = prompt | llm_service | parser

    result = chain.invoke({
        "ideal_candidate": ideal_candidate,
        "candidate": candidate
    })

    print(json.dumps(result, indent=2))

    return {
        "match_result": {
            "candidate_id": candidate["id"],
            "match_scores": result
        }
    }


def calculate_match_score(state: MatcherState):
    """
    Calculate the weighted overall candidate match score.
    """

    match_result = state["match_result"]
    match_scores = (
        match_result["match_scores"]
        if isinstance(match_result, dict)
        else match_result.match_scores
    )

    ideal_candidate = state["ideal_candidate"]
    evaluation_weights = (
        ideal_candidate["evaluation_weights"]
        if isinstance(ideal_candidate, dict)
        else ideal_candidate.evaluation_weights
    )

    validation_errors =  list(state.get("validation_errors", []))

    total_weight = sum(evaluation_weights.values())

    if total_weight <= 0:
        validation_errors.append("Total evaluation weight must be greater than zero.")

    overall_score = 0.0

    for section, weight in evaluation_weights.items():

        section_match = (
            match_scores.get(section)
            if isinstance(match_scores, dict)
            else getattr(match_scores, section, None)
        )

        if section_match is None:
            validation_errors.append(f"Missing match score for section: {section}")
            continue

        section_score = (
            section_match["score"]
            if isinstance(section_match, dict)
            else section_match.score
        )

        if not 0 <= section_score <= 100:
            validation_errors.append(f"Invalid score for section: {section}")
            continue

        if weight < 0:
            validation_errors.append(f"Invalid evaluation weight for section: {section}")
            continue

        if total_weight > 0:
            overall_score += section_score * (weight / total_weight)

        if not math.isclose(total_weight, 100.0, abs_tol=0.01):
            validation_errors.append(
                "Evaluation weights must sum to 100."
            )    

    return {
        "match_result": {
            **(
                match_result
                if isinstance(match_result, dict)
                else match_result.model_dump()
            ),
            "overall_score": (
                round(overall_score, 2)
                if not validation_errors
                else 0.0
            )
        },
        "validation_errors": validation_errors
    }







def validate_match_result(state: MatcherState):
    """
    Validate the completeness and integrity of the match result.
    """

    match_result = state["match_result"]

    if isinstance(match_result, dict):
        result = match_result
    else:
        result = match_result.model_dump()

    validation_errors = []

    required_sections = [
        "technical_skills",
        "soft_skills",
        "tech_stacks",
        "tools_and_platforms",
        "certifications",
        "work_experience",
        "coursework",
        "achievements",
        "education"
    ]

    # Validate candidate ID
    if not isinstance(result.get("candidate_id"), str) or not result["candidate_id"].strip():
        validation_errors.append("Invalid or missing candidate_id.")

    # Validate overall score
    overall_score = result.get("overall_score")

    if (
        not isinstance(overall_score, (int, float))
        or isinstance(overall_score, bool)
        or not math.isfinite(overall_score)
        or not 0 <= overall_score <= 100
    ):
        validation_errors.append("Invalid overall_score.")

    # Validate evaluation sections
    match_scores = result.get("match_scores")

    if not isinstance(match_scores, dict):
        validation_errors.append("Missing or invalid match_scores.")
    else:
        for section in required_sections:

            section_data = match_scores.get(section)

            if not isinstance(section_data, dict):
                validation_errors.append(f"Missing or invalid section: {section}")
                continue

            # Validate score
            score = section_data.get("score")

            if (
                not isinstance(score, (int, float))
                or isinstance(score, bool)
                or not math.isfinite(score)
                or not 0 <= score <= 100
            ):
                validation_errors.append(f"Invalid score in {section}.")

            # Validate justification
            justification = section_data.get("justification")

            if not isinstance(justification, str) or not justification.strip():
                validation_errors.append(f"Invalid justification in {section}.")

            # Validate list fields
            for field in ["matched_items", "missing_items", "evidence"]:

                value = section_data.get(field)

                if not isinstance(value, list) or not all(
                    isinstance(item, str) for item in value
                ):
                    validation_errors.append(
                        f"Invalid {field} in {section}."
                    )

    return {
        "validation_errors": validation_errors
    }






def validation_router(state: MatcherState):
    """
    Route based on validation results and retry count.
    """

    if not state["validation_errors"]:
        return "success"

    if state["retry_count"] < MAX_RETRIES:
        return "retry"

    return "failed"


def prepare_retry(state: MatcherState):
    """
    Prepare the state for another evaluation attempt.
    """

    return {
        "retry_count": state["retry_count"] + 1,
        "validation_errors": []
    }


def generate_ideal_candidate(state: MatcherState):
    """
    Generate an ideal candidate profile from the job description.
    """

    parser = JsonOutputParser(pydantic_object=IdealCandidate)

    prompt = ChatPromptTemplate.from_messages([
        ("system", generate_ideal_candidate_prompt),
        ("user", "Job Description: {job_description}")
    ])

    chain = prompt | llm_service | parser

    result = chain.invoke({
        "job_description": state["job_description"]
    })

    return {
        "ideal_candidate": result
    }



def get_ideal_candidate(state: MatcherState):
    """
    Retrieve the ideal candidate profile if available.
    """

    jd_id = state["jd_id"]

    db = LocalSession()

    try:
        ideal_candidate = (
            db.query(IdealCandidateModel)
            .filter(IdealCandidateModel.jd_id == jd_id)
            .first()
        )

        if ideal_candidate is None:
            return {"ideal_candidate": None}

        return {
            "ideal_candidate": {
                "technical_skills": ideal_candidate.technical_skills,
                "soft_skills": ideal_candidate.soft_skills,
                "tech_stacks": ideal_candidate.tech_stacks,
                "tools_and_platforms": ideal_candidate.tools_and_platforms,
                "certifications": ideal_candidate.certifications,
                "work_experience": ideal_candidate.work_experience,
                "coursework": ideal_candidate.coursework,
                "achievements": ideal_candidate.achievements,
                "education": ideal_candidate.education,
                "mandatory_requirements": ideal_candidate.mandatory_requirements,
                "preferred_requirements": ideal_candidate.preferred_requirements,
                "minimum_experience_years": ideal_candidate.minimum_experience_years,
                "required_education_level": ideal_candidate.required_education_level,
                "evaluation_weights": ideal_candidate.evaluation_weights
            }
        }

    finally:
        db.close()





def save_ideal_candidate(state: MatcherState):
    """
    Save the generated ideal candidate profile in the database.
    """

    jd_id = state["jd_id"]
    ideal_candidate = state["ideal_candidate"]

    db = LocalSession()

    try:
        db_ideal_candidate = IdealCandidateModel(
            jd_id=jd_id,
            **ideal_candidate
        )

        db.add(db_ideal_candidate)
        db.commit()
        db.refresh(db_ideal_candidate)

        return {
            "ideal_candidate": ideal_candidate
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()




def ideal_candidate_router(state: MatcherState):
    """
    Route based on the availability of an ideal candidate profile.
    """

    if state.get("ideal_candidate") is not None:
        return "match"

    return "generate"