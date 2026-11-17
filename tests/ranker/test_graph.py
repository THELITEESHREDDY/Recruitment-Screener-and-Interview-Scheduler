
import agents.ranker.nodes as ranker_nodes
from agents.ranker.graph import ranker_graph

from backend.models.candidate import Candidate
from backend.models.candidate_ranking import CandidateRanking
import pytest
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


def test_ranker_graph_end_to_end(db_setup, rubric_job, monkeypatch):

    # 1. Create a candidate in the test database.
    candidate = Candidate(
        name="Test Backend Candidate",
        email="backend@example.com",
        mobile_number="9876543210",
        google_form_response_id="graph-test-001"
    )

    db_setup.add(candidate)
    db_setup.commit()
    db_setup.refresh(candidate)

    # 2. Mock rubric generation.
    rubric = {
        "criteria": {
            "relevant_experience": {
                "weight": 0.4,
                "description": "Relevant backend experience.",
                "evaluation_guidelines": ["Assess backend experience."]
            },
            "project_impact": {
                "weight": 0.35,
                "description": "Impact of completed projects.",
                "evaluation_guidelines": ["Assess project outcomes."]
            },
            "problem_solving": {
                "weight": 0.25,
                "description": "Problem-solving ability.",
                "evaluation_guidelines": ["Assess problem-solving."]
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

    # 3. Mock the LLM evaluation response.
    evaluation = {
        "criteria_scores": {
            "relevant_experience": {
                "score": 85,
                "evidence_status": "sufficient",
                "justification": "Relevant backend experience."
            },
            "project_impact": {
                "score": 80,
                "evidence_status": "sufficient",
                "justification": "Good project outcomes."
            },
            "problem_solving": {
                "score": 75,
                "evidence_status": "partial",
                "justification": "Some problem-solving evidence."
            }
        },
        "overall_justification": "Strong evidence across the criteria."
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

    # 4. Construct the initial Ranker state.
    initial_state = {
        "jd_id": rubric_job.id,
        "job_description": rubric_job.job_description,

        "incoming_candidate": {
            "id": candidate.id,
            "name": candidate.name,
            "mobile_number": candidate.mobile_number,
            "email": candidate.email,
            "linkedin_url": "",
            "technical_skills": ["Python", "FastAPI", "SQL"],
            "soft_skills": ["Communication"],
            "tech_stacks": ["FastAPI"],
            "tools_and_platforms": [],
            "certifications": [],
            "work_experience": ["Backend development"],
            "coursework": ["DBMS", "Operating Systems"],
            "achievements": [],
            "education": "B.Tech Computer Science",
            "PEP_score": 80,
            "PEP_priority": 1
        },

        "match_result": {
            "candidate_id": candidate.id,
            "overall_score": 90,
            "match_scores": {
                "technical_skills": {
                    "score": 90,
                    "justification": "Strong Python and FastAPI skills.",
                    "matched_items": ["Python", "FastAPI"],
                    "missing_items": [],
                    "evidence": ["Built backend applications."]
                }
            }
        },

        "errors": []
    }

    # 5. Execute the complete graph.
    result = ranker_graph.invoke(initial_state)

    # 6. Verify graph execution.
    assert result["errors"] == []
    assert len(result["ranked_candidates"]) == 1

    ranked_candidate = result["ranked_candidates"][0]

    assert ranked_candidate["candidate_id"] == candidate.id
    assert ranked_candidate["overall_score"] == 90
    assert ranked_candidate["rank"] == 1

    # 7. Verify database persistence.
    saved_record = (
        db_setup.query(CandidateRanking)
        .filter(
            CandidateRanking.jd_id == rubric_job.id,
            CandidateRanking.candidate_id == candidate.id
        )
        .first()
    )

    assert saved_record is not None
    assert saved_record.overall_score == 90
    assert saved_record.rank == 1
    assert saved_record.secondary_score > 0




def test_ranker_graph_updates_leaderboard_for_multiple_candidates(
    db_setup, rubric_job, monkeypatch
):
    from backend.models.candidate import Candidate
    from backend.models.candidate_ranking import CandidateRanking
    import agents.ranker.nodes as ranker_nodes
    from agents.ranker.graph import ranker_graph

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

    candidates_data = [
        ("Candidate A", "a@example.com", "multi-a", 85),
        ("Candidate B", "b@example.com", "multi-b", 95),
        ("Candidate C", "c@example.com", "multi-c", 90),
    ]

    candidate_ids = []

    for name, email, response_id, match_score in candidates_data:
        candidate = Candidate(
            name=name,
            email=email,
            mobile_number="9876543210",
            google_form_response_id=response_id
        )

        db_setup.add(candidate)
        db_setup.commit()
        db_setup.refresh(candidate)

        candidate_ids.append(candidate.id)

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

        result = ranker_graph.invoke(state)

        assert result["errors"] == []

    # Final leaderboard should be ordered by Matcher score.
    final_result = result["ranked_candidates"]

    assert len(final_result) == 3

    assert [
        item["overall_score"] for item in final_result
    ] == [95, 90, 85]

    assert [
        item["candidate_id"] for item in final_result
    ] == [
        candidate_ids[1],
        candidate_ids[2],
        candidate_ids[0]
    ]

    assert [
        item["rank"] for item in final_result
    ] == [1, 2, 3]

    # Verify database contains exactly three records.
    saved_records = (
        db_setup.query(CandidateRanking)
        .filter(CandidateRanking.jd_id == rubric_job.id)
        .all()
    )

    assert len(saved_records) == 3

    assert len({
        record.candidate_id for record in saved_records
    }) == 3




def test_rank_candidates_applies_competition_ranking_and_tiebreaker():
    from agents.ranker.nodes import rank_candidates

    existing_candidates = [
        {
            "candidate_id": "candidate-a",
            "overall_score": 95,
            "secondary_score": 80,
            "match_scores": {},
            "secondary_details": {},
            "rank": 0,
            "one_line_rationale": "A"
        },
        {
            "candidate_id": "candidate-b",
            "overall_score": 92,
            "secondary_score": 90,
            "match_scores": {},
            "secondary_details": {},
            "rank": 0,
            "one_line_rationale": "B"
        },
        {
            "candidate_id": "candidate-c",
            "overall_score": 92,
            "secondary_score": 90,
            "match_scores": {},
            "secondary_details": {},
            "rank": 0,
            "one_line_rationale": "C"
        },
        {
            "candidate_id": "candidate-d",
            "overall_score": 92,
            "secondary_score": 85,
            "match_scores": {},
            "secondary_details": {},
            "rank": 0,
            "one_line_rationale": "D"
        }
    ]

    state = {
        "existing_candidates": existing_candidates,
        "incoming_candidate": {
            "id": "candidate-e",
            "name": "Candidate E"
        },
        "match_result": {
            "candidate_id": "candidate-e",
            "overall_score": 87,
            "match_scores": {}
        },
        "secondary_evaluation": {
            "weighted_score": 95,
            "overall_justification": "Strong candidate."
        },
        "errors": []
    }

    result = rank_candidates(state)

    ranked = result["ranked_candidates"]

    assert [
        candidate["candidate_id"] for candidate in ranked
    ] == [
        "candidate-a",
        "candidate-b",
        "candidate-c",
        "candidate-d",
        "candidate-e"
    ]

    assert [
        candidate["rank"] for candidate in ranked
    ] == [1, 2, 2, 4, 5]

