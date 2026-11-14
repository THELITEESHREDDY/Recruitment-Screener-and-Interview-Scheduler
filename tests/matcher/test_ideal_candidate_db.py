
import uuid

import pytest

from agents.db.connection import LocalSession
from agents.db.models import JobDescription, IdealCandidateModel
from agents.matcher.nodes import (
    get_ideal_candidate,
    save_ideal_candidate,
    ideal_candidate_router
)


@pytest.fixture
def db_setup():
    db = LocalSession()

    jd = JobDescription(
        job_description="Python Backend Developer"
    )

    db.add(jd)
    db.commit()
    db.refresh(jd)

    yield db, jd.id

    # Cleanup
    db.query(IdealCandidateModel).filter(
        IdealCandidateModel.jd_id == jd.id
    ).delete()

    db.query(JobDescription).filter(
        JobDescription.id == jd.id
    ).delete()

    db.commit()
    db.close()


@pytest.fixture
def ideal_candidate():
    return {
        "technical_skills": ["Python", "DSA"],
        "soft_skills": ["Communication"],
        "tech_stacks": ["FastAPI", "PostgreSQL"],
        "tools_and_platforms": ["Git", "Docker"],
        "certifications": [],
        "work_experience": ["1 year backend development"],
        "coursework": ["DBMS", "Operating Systems"],
        "achievements": ["Hackathon finalist"],
        "education": "B.Tech Computer Science",
        "mandatory_requirements": ["Python", "FastAPI"],
        "preferred_requirements": ["Docker"],
        "minimum_experience_years": 1.0,
        "required_education_level": "Bachelor's degree",
        "evaluation_weights": {
            "technical_skills": 25.0,
            "soft_skills": 5.0,
            "tech_stacks": 20.0,
            "tools_and_platforms": 10.0,
            "certifications": 0.0,
            "work_experience": 20.0,
            "coursework": 5.0,
            "achievements": 5.0,
            "education": 10.0
        }
    }


def test_first_candidate_generates_and_saves_profile(
    db_setup,
    ideal_candidate
):
    db, jd_id = db_setup

    state = {"jd_id": jd_id}

    # First lookup should return None.
    result = get_ideal_candidate(state)

    assert result["ideal_candidate"] is None

    # Generate and save the profile.
    state["ideal_candidate"] = ideal_candidate

    save_ideal_candidate(state)

    # Verify that the record exists in SQLite.
    saved_profile = db.query(IdealCandidateModel).filter(
        IdealCandidateModel.jd_id == jd_id
    ).first()

    assert saved_profile is not None
    assert saved_profile.evaluation_weights == ideal_candidate["evaluation_weights"]


def test_second_candidate_reuses_existing_profile(
    db_setup,
    ideal_candidate
):
    db, jd_id = db_setup

    # Save profile generated for the first candidate.
    save_ideal_candidate({
        "jd_id": jd_id,
        "ideal_candidate": ideal_candidate
    })

    # Second candidate uses the same JD.
    result = get_ideal_candidate({
        "jd_id": jd_id
    })

    assert result["ideal_candidate"] is not None
    assert result["ideal_candidate"] == ideal_candidate

    # Existing profile should route directly to matching.
    assert ideal_candidate_router(result) == "match"


def test_different_jd_generates_new_profile(
    db_setup,
    ideal_candidate
):
    db, first_jd_id = db_setup

    # Save profile for the first JD.
    save_ideal_candidate({
        "jd_id": first_jd_id,
        "ideal_candidate": ideal_candidate
    })

    # Create another JD.
    second_jd = JobDescription(
        job_description="Java Backend Developer"
    )

    db.add(second_jd)
    db.commit()
    db.refresh(second_jd)

    try:
        result = get_ideal_candidate({
            "jd_id": second_jd.id
        })

        assert result["ideal_candidate"] is None
        assert ideal_candidate_router(result) == "generate"

    finally:
        db.query(IdealCandidateModel).filter(
            IdealCandidateModel.jd_id == second_jd.id
        ).delete()

        db.delete(second_jd)
        db.commit()