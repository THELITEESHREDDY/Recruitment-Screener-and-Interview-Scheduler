import pytest
from agents.matcher.nodes import match_candidate


@pytest.fixture
def matcher_state():
    return {
        "jd_id": "JD-001",

        "ideal_candidate": {
            "technical_skills": [
                "Python",
                "SQL",
                "REST API Development"
            ],
            "soft_skills": [
                "Communication",
                "Problem Solving"
            ],
            "tech_stacks": [
                "FastAPI",
                "PostgreSQL"
            ],
            "tools_and_platforms": [
                "Git",
                "Docker"
            ],
            "certifications": [
                "AWS Certified Developer"
            ],
            "work_experience": [
                "2 years of backend development",
                "Experience building REST APIs"
            ],
            "coursework": [
                "DBMS",
                "Operating Systems"
            ],
            "achievements": [
                "Backend development projects"
            ],
            "education": "Bachelor's degree in Computer Science",

            "mandatory_requirements": [
                "Python",
                "REST API Development",
                "2 years of backend experience"
            ],
            "preferred_requirements": [
                "Docker",
                "AWS Certification"
            ],
            "minimum_experience_years": 2.0,
            "required_education_level": "Bachelor's degree",

            "evaluation_weights": {
                "technical_skills": 25,
                "work_experience": 20,
                "tech_stacks": 15,
                "education": 10,
                "tools_and_platforms": 10,
                "soft_skills": 5,
                "certifications": 5,
                "coursework": 5,
                "achievements": 5
            }
        },

        "candidate": {
            "id": "CAND-001",
            "name": "John Doe",
            "mobile_number": "9876543210",
            "email": "john@example.com",
            "linkedin_url": "https://linkedin.com/in/johndoe",

            "technical_skills": [
                "Python",
                "SQL",
                "C++"
            ],
            "soft_skills": [
                "Problem Solving",
                "Teamwork"
            ],
            "tech_stacks": [
                "FastAPI",
                "MySQL"
            ],
            "tools_and_platforms": [
                "Git",
                "VS Code"
            ],
            "certifications": [],
            "work_experience": [
                "Developed REST APIs using FastAPI",
                "Completed backend development internship for 6 months"
            ],
            "coursework": [
                "DBMS",
                "Operating Systems"
            ],
            "achievements": [
                "Built a backend project using FastAPI"
            ],
            "education": "B.Tech Computer Science",

            "PEP_score": 75,
            "PEP_priority": 2
        },

        "retry_count": 0,
        "validation_errors": []
    }


def test_match_candidate(matcher_state):

    result = match_candidate(matcher_state)

    assert "match_result" in result

    match_scores = result["match_result"]["match_scores"]

    expected_sections = [
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

    assert set(match_scores.keys()) == set(expected_sections)

    for section in expected_sections:

        section_result = match_scores[section]

        assert 0 <= section_result["score"] <= 100

        assert isinstance(section_result["justification"], str)
        assert isinstance(section_result["matched_items"], list)
        assert isinstance(section_result["missing_items"], list)
        assert isinstance(section_result["evidence"], list)
