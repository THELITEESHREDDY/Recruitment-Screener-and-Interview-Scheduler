import pytest

from agents.matcher.nodes import calculate_match_score


def test_calculate_match_score():

    state = {
        "match_result": {
            "match_scores": {
                "technical_skills": {"score": 80},
                "soft_skills": {"score": 70},
                "tech_stacks": {"score": 90},
                "tools_and_platforms": {"score": 80},
                "certifications": {"score": 60},
                "work_experience": {"score": 70},
                "coursework": {"score": 90},
                "achievements": {"score": 85},
                "education": {"score": 90}
            }
        },

        "ideal_candidate": {
            "evaluation_weights": {
                "technical_skills": 25,
                "soft_skills": 10,
                "tech_stacks": 15,
                "tools_and_platforms": 10,
                "certifications": 5,
                "work_experience": 15,
                "coursework": 5,
                "achievements": 5,
                "education": 10
            }
        }
    }

    result = calculate_match_score(state)
    assert result["match_result"]["overall_score"] == 79.75, result["validation_errors"]

    assert result["match_result"]["overall_score"] == 79.75