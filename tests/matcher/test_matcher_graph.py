import uuid
import pytest
import json
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from agents.matcher.graph import matcher_graph
from agents.db.connection import LocalSession
from agents.db.models import JobDescription, IdealCandidateModel
from agents.matcher import nodes





#helpers
SECTIONS = [
    "technical_skills",
    "soft_skills",
    "tech_stacks",
    "tools_and_platforms",
    "certifications",
    "work_experience",
    "coursework",
    "achievements",
    "education",
]


def valid_match_scores():
    return {
        section: {
            "score": 80.0,
            "justification": f"Evidence supports {section}.",
            "matched_items": ["Python"],
            "missing_items": [],
            "evidence": ["Candidate profile"],
        }
        for section in SECTIONS
    }


def invalid_match_scores():
    result = valid_match_scores()
    result["technical_skills"]["justification"] = ""
    return result


def save_test_ideal_candidate(jd_id):
    profile = {
        "technical_skills": ["Python"],
        "soft_skills": ["Communication"],
        "tech_stacks": ["FastAPI"],
        "tools_and_platforms": ["Git"],
        "certifications": [],
        "work_experience": ["1 year Python development"],
        "coursework": ["DBMS"],
        "achievements": [],
        "education": "B.Tech Computer Science",
        "mandatory_requirements": ["Python"],
        "preferred_requirements": ["FastAPI"],
        "minimum_experience_years": 1.0,
        "required_education_level": "Bachelor's degree",
        "evaluation_weights": {
            "technical_skills": 20,
            "soft_skills": 10,
            "tech_stacks": 15,
            "tools_and_platforms": 10,
            "certifications": 5,
            "work_experience": 15,
            "coursework": 5,
            "achievements": 5,
            "education": 15,
        },
    }

    db = LocalSession()

    try:
        db.add(IdealCandidateModel(jd_id=jd_id, **profile))
        db.commit()
    finally:
        db.close()


def matcher_test_input(jd_id, candidate):
    return {
        "jd_id": jd_id,
        "job_description": "Test job description",
        "candidate": candidate,
        "retry_count": 0,
        "validation_errors": [],
    }


def test_matcher_stops_after_max_retries(
    db_setup, candidate, monkeypatch
):
    save_test_ideal_candidate(db_setup)

    calls = 0

    def fake_llm(_messages):
        nonlocal calls
        calls += 1

        return AIMessage(
            content=json.dumps(invalid_match_scores())
        )

    monkeypatch.setattr(
        nodes,
        "llm_service",
        RunnableLambda(fake_llm)
    )

    result = matcher_graph.invoke(
        matcher_test_input(db_setup, candidate)
    )

    assert calls == 3
    assert result["retry_count"] == 2
    assert result["validation_errors"]



def test_matcher_retries_once_then_succeeds(
    db_setup, candidate, monkeypatch
):
    save_test_ideal_candidate(db_setup)

    responses = [
        invalid_match_scores(),
        valid_match_scores(),
    ]

    calls = 0

    def fake_llm(_messages):
        nonlocal calls

        response = responses[calls]
        calls += 1

        return AIMessage(content=json.dumps(response))

    monkeypatch.setattr(
        nodes,
        "llm_service",
        RunnableLambda(fake_llm)
    )

    result = matcher_graph.invoke(
        matcher_test_input(db_setup, candidate)
    )

    assert calls == 2
    assert result["retry_count"] == 1
    assert result["validation_errors"] == []
    assert result["match_result"]["candidate_id"] == candidate["id"]




@pytest.fixture
def db_setup():
    db = LocalSession()

    jd = JobDescription(
        job_description="""
        We are hiring a Python Backend Developer.

        Requirements:
        - Strong Python programming skills.
        - Experience with FastAPI and REST APIs.
        - Knowledge of SQL and PostgreSQL.
        - Understanding of data structures and algorithms.
        - Familiarity with Git and Docker.
        - Good problem-solving and communication skills.
        - Bachelor's degree in Computer Science or equivalent.
        - 1+ years of backend development experience.
        """
    )

    db.add(jd)
    db.commit()
    db.refresh(jd)

    yield jd.id

    db.query(IdealCandidateModel).filter(
        IdealCandidateModel.jd_id == jd.id
    ).delete()

    db.delete(jd)
    db.commit()
    db.close()


@pytest.fixture
def candidate():
    return {
        "id": str(uuid.uuid4()),
        "name": "Rahul Sharma",
        "mobile_number": "9876543210",
        "email": "rahul@example.com",
        "linkedin_url": "https://linkedin.com/in/rahul",

        "technical_skills": [
            "Python",
            "SQL",
            "Data Structures",
            "REST API Development"
        ],

        "soft_skills": [
            "Communication",
            "Problem Solving",
            "Teamwork"
        ],

        "tech_stacks": [
            "FastAPI",
            "PostgreSQL"
        ],

        "tools_and_platforms": [
            "Git",
            "Docker",
            "VS Code"
        ],

        "certifications": [],

        "work_experience": [
            "1 year of Python backend development experience",
            "Developed REST APIs using FastAPI"
        ],

        "coursework": [
            "Database Management Systems",
            "Operating Systems",
            "Data Structures and Algorithms"
        ],

        "achievements": [
            "Developed and deployed backend projects"
        ],

        "education": "B.Tech Computer Science",

        "PEP_score": 80,
        "PEP_priority": 2
    }


def test_complete_matcher_graph(db_setup, candidate):

    initial_state = {
        "jd_id": db_setup,
        "job_description": """
        We are hiring a Python Backend Developer.

        Requirements:
        - Strong Python programming skills.
        - Experience with FastAPI and REST APIs.
        - Knowledge of SQL and PostgreSQL.
        - Understanding of data structures and algorithms.
        - Familiarity with Git and Docker.
        - Good problem-solving and communication skills.
        - Bachelor's degree in Computer Science or equivalent.
        - 1+ years of backend development experience.
        """,
        "candidate": candidate,
        "retry_count": 0,
        "validation_errors": []
    }

    result = matcher_graph.invoke(initial_state)

    # Verify match result
    assert "match_result" in result

    match_result = result["match_result"]

    assert match_result["candidate_id"] == candidate["id"]

    assert 0 <= match_result["overall_score"] <= 100

    # Verify all evaluation sections
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

    for section in required_sections:
        assert section in match_result["match_scores"]
        assert 0 <= match_result["match_scores"][section]["score"] <= 100

    # Verify validation
    assert result["validation_errors"] == []

    # Verify ideal candidate was saved
    db = LocalSession()

    try:
        saved_profile = (
            db.query(IdealCandidateModel)
            .filter(IdealCandidateModel.jd_id == db_setup)
            .first()
        )

        assert saved_profile is not None
        assert saved_profile.evaluation_weights is not None

    finally:
        db.close()





def test_reuse_ideal_candidate_for_same_jd(db_setup, candidate):

    # First candidate: generates and saves the profile
    first_state = {
        "jd_id": db_setup,
        "job_description": "Python Backend Developer with FastAPI and PostgreSQL experience.",
        "candidate": candidate,
        "retry_count": 0,
        "validation_errors": []
    }

    first_result = matcher_graph.invoke(first_state)

    assert first_result["validation_errors"] == []

    # Second candidate: reuse the same JD profile
    second_candidate = {
        **candidate,
        "id": str(uuid.uuid4()),
        "name": "Arjun Kumar",
        "email": "arjun@example.com"
    }

    second_state = {
        **first_state,
        "candidate": second_candidate
    }

    second_result = matcher_graph.invoke(second_state)

    assert second_result["validation_errors"] == []
    assert second_result["match_result"]["candidate_id"] == second_candidate["id"]

    # Verify only one ideal candidate exists for this JD
    db = LocalSession()

    try:
        count = db.query(IdealCandidateModel).filter(
            IdealCandidateModel.jd_id == db_setup
        ).count()

        assert count == 1

    finally:
        db.close()



def test_generate_new_ideal_candidate_for_different_jd(db_setup, candidate):

    original_state = {
        "jd_id": db_setup,
        "job_description": """
        We are hiring a Python Backend Developer.

        Requirements:
        - Strong Python programming skills.
        - Experience with FastAPI and REST APIs.
        - Knowledge of SQL and PostgreSQL.
        - Understanding of data structures and algorithms.
        - Familiarity with Git and Docker.
        - Good problem-solving and communication skills.
        - Bachelor's degree in Computer Science or equivalent.
        - 1+ years of backend development experience.
        """,
        "candidate": candidate,
        "retry_count": 0,
        "validation_errors": []
    }

    original_result = matcher_graph.invoke(original_state)

    assert original_result["validation_errors"] == []

    db = LocalSession()

    try:
        new_jd = JobDescription(
            job_description="""
            We are hiring a React Frontend Developer.

            Requirements:
            - Strong JavaScript and TypeScript.
            - React and Next.js experience.
            - HTML, CSS and responsive design.
            - REST API integration.
            - Git and frontend development experience.
            - Bachelor's degree in Computer Science.
            """
        )

        db.add(new_jd)
        db.commit()
        db.refresh(new_jd)

        new_jd_id = new_jd.id

    finally:
        db.close()

    initial_state = {
        "jd_id": new_jd_id,
        "job_description": new_jd.job_description,
        "candidate": candidate,
        "retry_count": 0,
        "validation_errors": []
    }

    result = matcher_graph.invoke(initial_state)

    assert result["validation_errors"] == []
    assert result["match_result"]["candidate_id"] == candidate["id"]

    db = LocalSession()

    try:
        profiles = db.query(IdealCandidateModel).filter(
            IdealCandidateModel.jd_id == new_jd_id
        ).count()

        assert profiles == 1

        # The original JD should also retain its own profile.
        original_profiles = db.query(IdealCandidateModel).filter(
            IdealCandidateModel.jd_id == db_setup
        ).count()

        assert original_profiles == 1

    finally:
        db.query(IdealCandidateModel).filter(
            IdealCandidateModel.jd_id == new_jd_id
        ).delete()

        db.query(JobDescription).filter(
            JobDescription.id == new_jd_id
        ).delete()

        db.commit()
        db.close()