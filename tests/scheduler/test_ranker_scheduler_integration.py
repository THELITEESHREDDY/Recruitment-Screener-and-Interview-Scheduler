
import pytest

from backend.models.candidate import Candidate

import agents.ranker.nodes as ranker_nodes
from agents.ranker.graph import ranker_graph

from agents.scheduler.adapter import adapt_ranked_candidates
from agents.scheduler.graph import scheduler_graph
from agents.scheduler.tools.booking import booked_slots
from backend.models.job import JobDescription



@pytest.fixture
def rubric_job(db_setup):
    job = JobDescription(
        id="graph-test-jd-001",
        job_description=(
            "Backend Developer with Python, FastAPI, "
            "SQL and problem-solving skills."
        )
    )

    db_setup.add(job)
    db_setup.commit()
    db_setup.refresh(job)

    return job


@pytest.fixture(autouse=True)
def reset_booked_slots():
    booked_slots.clear()
    yield
    booked_slots.clear()

def test_ranker_scheduler_integration(db_setup, rubric_job, monkeypatch):

    # 1. Mock secondary rubric generation.
    rubric = {
        "criteria": {
            "relevant_experience": {
                "weight": 0.4,
                "description": "Relevant experience",
                "evaluation_guidelines": ["Assess experience"]
            },
            "project_impact": {
                "weight": 0.35,
                "description": "Project impact",
                "evaluation_guidelines": ["Assess impact"]
            },
            "problem_solving": {
                "weight": 0.25,
                "description": "Problem solving",
                "evaluation_guidelines": ["Assess problem solving"]
            }
        }
    }

    monkeypatch.setattr(
        ranker_nodes,
        "generate_secondary_rubric",
        lambda state: {
            "secondary_rubric": rubric,
            "errors": []
        }
    )

    # 2. Mock LLM evaluation.
    evaluation = {
        "criteria_scores": {
            "relevant_experience": {
                "score": 80,
                "evidence_status": "sufficient",
                "justification": "Relevant experience."
            },
            "project_impact": {
                "score": 80,
                "evidence_status": "sufficient",
                "justification": "Good project impact."
            },
            "problem_solving": {
                "score": 80,
                "evidence_status": "sufficient",
                "justification": "Good problem solving."
            }
        },
        "overall_justification": "Good overall evidence."
    }

    class MockChain:
        def __or__(self, other):
            return self

        def invoke(self, inputs):
            return evaluation

    class MockPrompt:
        def __or__(self, other):
            return MockChain()

    monkeypatch.setattr(
        ranker_nodes.ChatPromptTemplate,
        "from_messages",
        lambda messages: MockPrompt()
    )

    # 3. Prepare candidates.
    candidates_data = [
        ("Candidate A", "a@example.com", "integration-a", 85),
        ("Candidate B", "b@example.com", "integration-b", 95),
        ("Candidate C", "c@example.com", "integration-c", 90),
    ]

    # 4. Run Ranker for each candidate.
    ranked_candidates = []

    for name, email, response_id, match_score in candidates_data:

        candidate = Candidate(
            name=name,
            email=email,
            mobile_number=f"98765432{len(ranked_candidates):02d}",
            google_form_response_id=response_id
        )

        db_setup.add(candidate)
        db_setup.commit()
        db_setup.refresh(candidate)

        state = {
            "jd_id": rubric_job.id,
            "job_description": rubric_job.job_description,

            "incoming_candidate": {
                "id": candidate.id,
                "name": candidate.name,
                "mobile_number": candidate.mobile_number,
                "email": candidate.email,
                "linkedin_url": "",
                "technical_skills": ["Python", "FastAPI"],
                "soft_skills": ["Communication"],
                "tech_stacks": ["FastAPI"],
                "tools_and_platforms": [],
                "certifications": [],
                "work_experience": ["Backend development"],
                "coursework": ["DBMS"],
                "achievements": [],
                "education": "B.Tech Computer Science",
                "PEP_score": 80,
                "PEP_priority": 1
            },

            "match_result": {
                "candidate_id": candidate.id,
                "overall_score": match_score,
                "match_scores": {
                    "technical_skills": {
                        "score": match_score,
                        "justification": "Good technical skills.",
                        "matched_items": ["Python", "FastAPI"],
                        "missing_items": [],
                        "evidence": ["Backend project experience."]
                    }
                }
            },

            "errors": []
        }

        ranker_result = ranker_graph.invoke(state)

        assert ranker_result["errors"] == []

    # 5. Get the final ranked leaderboard.
    ranked_candidates = ranker_result["ranked_candidates"]

    assert len(ranked_candidates) == 3

    assert [
        item["overall_score"] for item in ranked_candidates
    ] == [95, 90, 85]

    assert [
        item["rank"] for item in ranked_candidates
    ] == [1, 2, 3]

    # 6. Adapt Ranker output for Scheduler.
    scheduler_candidates = adapt_ranked_candidates(
        ranked_candidates
    )

    # 7. Invoke Scheduler.
    scheduler_input = {
        "ranked_candidates": scheduler_candidates,
        "top_n": 3,
        "selected_candidates": [],
        "available_slots": [],
        "schedule": [],
        "errors": []
    }

    scheduler_result = scheduler_graph.invoke(scheduler_input)

    # 8. Verify Ranker -> Scheduler integration.
    assert len(scheduler_result["schedule"]) == 3

    assert [
        item["candidate_id"]
        for item in scheduler_result["schedule"]
    ] == [
        item["candidate_id"]
        for item in ranked_candidates
    ]

    assert all(
        item["status"] == "confirmed"
        for item in scheduler_result["schedule"]
    )