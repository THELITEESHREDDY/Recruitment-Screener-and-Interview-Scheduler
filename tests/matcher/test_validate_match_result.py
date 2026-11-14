import pytest

from agents.matcher.nodes import validate_match_result

# Test	                       Expected behavior
# Valid result	              Empty error list
# Missing section          	  Detect missing section
# Invalid section score	      Detect score outside 0–100
# Missing justification	      Detect empty justification
# Invalid evidence      	  Detect non-list evidence
# Invalid overall score	      Detect score outside 0–100
def get_valid_state():

    sections = [
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

    match_scores = {}

    for section in sections:
        match_scores[section] = {
            "score": 85,
            "justification": "Good alignment with the requirements.",
            "matched_items": ["Python", "FastAPI"],
            "missing_items": ["Docker"],
            "evidence": ["Used Python in a backend project."]
        }

    return {
        "match_result": {
            "candidate_id": "candidate_001",
            "match_scores": match_scores,
            "overall_score": 85.0
        }
    }


def test_valid_match_result():

    state = get_valid_state()

    result = validate_match_result(state)

    assert result["validation_errors"] == []


def test_missing_evaluation_section():

    state = get_valid_state()

    del state["match_result"]["match_scores"]["technical_skills"]

    result = validate_match_result(state)

    assert "Missing or invalid section: technical_skills" in result["validation_errors"]


def test_invalid_section_score():

    state = get_valid_state()

    state["match_result"]["match_scores"]["technical_skills"]["score"] = 150

    result = validate_match_result(state)

    assert "Invalid score in technical_skills." in result["validation_errors"]


def test_missing_justification():

    state = get_valid_state()

    state["match_result"]["match_scores"]["technical_skills"]["justification"] = ""

    result = validate_match_result(state)

    assert "Invalid justification in technical_skills." in result["validation_errors"]


def test_invalid_evidence_format():

    state = get_valid_state()

    state["match_result"]["match_scores"]["technical_skills"]["evidence"] = "Python project"

    result = validate_match_result(state)

    assert "Invalid evidence in technical_skills." in result["validation_errors"]


def test_invalid_overall_score():

    state = get_valid_state()

    state["match_result"]["overall_score"] = 120

    result = validate_match_result(state)

    assert "Invalid overall_score." in result["validation_errors"]