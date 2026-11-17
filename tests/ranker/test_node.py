import pytest
from backend.db.init_db import initialize_database
from agents.ranker.nodes import (calculate_secondary_score,evaluate_secondary_metrics, load_existing_rankings,rank_candidates)
from backend.models.candidate import Candidate
initialize_database()
from agents.ranker.nodes import persist_rankings
from backend.models.candidate_ranking import CandidateRanking
import agents.ranker.nodes as ranker_nodes


@pytest.mark.integration
def test_evaluate_secondary_metrics_captures_llm_error(monkeypatch):


    def mock_llm_failure(*args, **kwargs):
        raise RuntimeError("Simulated LLM failure")

    monkeypatch.setattr(
        ranker_nodes,
        "llm_service",
        mock_llm_failure
    )

    state = {
        "incoming_candidate": {
            "id": "candidate_x"
        },
        "match_result": {
            "candidate_id": "candidate_x",
            "overall_score": 80,
            "match_scores": {}
        },
        "secondary_rubric": {
            "criteria": {
                "relevant_experience": {
                    "weight": 1.0,
                    "description": "Relevant experience",
                    "evaluation_guidelines": ["Assess experience."]
                }
            }
        },
        "errors": []
    }    
    result = ranker_nodes.evaluate_secondary_metrics(state)

    assert "secondary_evaluation" not in result
    assert len(result["errors"]) == 1
    assert result["errors"][0]["node"] == "evaluate_secondary_metrics"
    assert result["errors"][0]["retryable"] is True





def test_calculate_secondary_score_captures_invalid_weight():

    state = {
        "secondary_rubric": {
            "criteria": {
                "experience": {"weight": -0.4},
                "projects": {"weight": 0.6}
            }
        },
        "secondary_evaluation": {
            "criteria_scores": {
                "experience": {
                    "score": 80,
                    "evidence_status": "sufficient",
                    "justification": "Good experience."
                },
                "projects": {
                    "score": 70,
                    "evidence_status": "sufficient",
                    "justification": "Good projects."
                }
            },
            "overall_justification": "Evaluation completed."
        }
    }

    result = calculate_secondary_score(state)

    assert "secondary_evaluation" not in result
    assert len(result["errors"]) == 1
    assert result["errors"][0]["error_type"] == "invalid_weight"
    assert result["errors"][0]["retryable"] is False


def test_calculate_secondary_score_preserves_existing_errors():

    existing_error = {
        "node": "evaluate_secondary_metrics",
        "error_type": "llm_error",
        "message": "LLM request failed.",
        "retryable": True
    }

    state = {
        "errors": [existing_error],
        "secondary_rubric": {
            "criteria": {
                "experience": {"weight": 1.0}
            }
        },
        "secondary_evaluation": {
            "criteria_scores": {
                "experience": {
                    "score": 80,
                    "evidence_status": "sufficient",
                    "justification": "Good experience."
                }
            },
            "overall_justification": "Evaluation completed."
        }
    }

    result = calculate_secondary_score(state)

    assert result["errors"] == [existing_error]




import pytest

from agents.ranker import nodes as ranker_nodes
from backend.models.job import JobDescription
from backend.models.job_ranking_rubrik import JobRankingRubric


@pytest.fixture
def rubric_job(db_setup):
    """
    Create a job description for rubric tests.
    """

    session = db_setup

    job = JobDescription(
        id="test-rubric-jd-001",
        job_description=(
            "Backend Developer with Python, FastAPI, "
            "SQL and problem-solving skills."
        )
    )

    session.add(job)
    session.commit()

    return job


@pytest.fixture
def sample_rubric():
    return {
        "criteria": {
            "relevant_experience": {
                "weight": 0.4,
                "description": "Relevant backend experience.",
                "evaluation_guidelines": [
                    "Assess experience with backend development."
                ]
            },
            "project_impact": {
                "weight": 0.35,
                "description": "Impact demonstrated through projects.",
                "evaluation_guidelines": [
                    "Assess practical project outcomes."
                ]
            },
            "problem_solving": {
                "weight": 0.25,
                "description": "Problem-solving ability.",
                "evaluation_guidelines": [
                    "Assess analytical problem-solving evidence."
                ]
            }
        }
    }


def test_retrieve_existing_rubric(
    db_setup,
    rubric_job,
    sample_rubric,
    monkeypatch
):

    session = db_setup

    session.add(
        JobRankingRubric(
            jd_id=rubric_job.id,
            criteria=sample_rubric["criteria"]
        )
    )
    session.commit()

    def mock_generation(state):
        pytest.fail("LLM should not be called for an existing rubric.")

    monkeypatch.setattr(
        ranker_nodes,
        "generate_secondary_rubric",
        mock_generation
    )

    result = ranker_nodes.get_or_create_secondary_rubric({
        "jd_id": rubric_job.id,
        "errors": []
    })

    assert result["secondary_rubric"] == sample_rubric
    assert result["errors"] == []


def test_generate_and_save_new_rubric(
    db_setup,
    rubric_job,
    sample_rubric,
    monkeypatch
):

    session = db_setup

    def mock_generation(state):

        assert state["jd_id"] == rubric_job.id
        assert state["job_description"] == rubric_job.job_description

        return {
            "secondary_rubric": sample_rubric,
            "errors": []
        }

    monkeypatch.setattr(
        ranker_nodes,
        "generate_secondary_rubric",
        mock_generation
    )

    result = ranker_nodes.get_or_create_secondary_rubric({
        "jd_id": rubric_job.id,
        "errors": []
    })

    assert result["secondary_rubric"] == sample_rubric
    assert result["errors"] == []

    saved_rubric = (
        session.query(JobRankingRubric)
        .filter(JobRankingRubric.jd_id == rubric_job.id)
        .first()
    )

    assert saved_rubric is not None
    assert saved_rubric.criteria == sample_rubric["criteria"]


def test_repeated_request_reuses_saved_rubric(
    db_setup,
    rubric_job,
    sample_rubric,
    monkeypatch
):

    session = db_setup
    generation_calls = 0

    def mock_generation(state):

        nonlocal generation_calls
        generation_calls += 1

        return {
            "secondary_rubric": sample_rubric,
            "errors": []
        }

    monkeypatch.setattr(
        ranker_nodes,
        "generate_secondary_rubric",
        mock_generation
    )

    state = {
        "jd_id": rubric_job.id,
        "errors": []
    }

    # First request: generate and persist.
    first_result = ranker_nodes.get_or_create_secondary_rubric(state)

    # Second request: retrieve existing rubric.
    second_result = ranker_nodes.get_or_create_secondary_rubric(state)

    assert first_result["secondary_rubric"] == sample_rubric
    assert second_result["secondary_rubric"] == sample_rubric

    assert generation_calls == 1

    rubric_count = (
        session.query(JobRankingRubric)
        .filter(JobRankingRubric.jd_id == rubric_job.id)
        .count()
    )

    assert rubric_count == 1


def test_missing_job_description_returns_error():

    result = ranker_nodes.get_or_create_secondary_rubric({
        "jd_id": "non-existent-jd",
        "errors": []
    })

    assert "secondary_rubric" not in result
    assert len(result["errors"]) == 1

    assert (
        result["errors"][0]["error_type"]
        == "job_description_not_found"
    )

    assert result["errors"][0]["retryable"] is False



def test_evaluate_secondary_metrics_success(monkeypatch):

    import agents.ranker.nodes as ranker_nodes

    expected_evaluation = {
        "criteria_scores": {
            "relevant_experience": {
                "score": 85,
                "evidence_status": "sufficient",
                "justification": "Candidate has relevant backend experience."
            },
            "project_impact": {
                "score": 75,
                "evidence_status": "partial",
                "justification": "Candidate has projects with limited impact evidence."
            },
            "problem_solving": {
                "score": 50,
                "evidence_status": "insufficient",
                "justification": "Not enough evidence to assess problem-solving."
            }
        },
        "overall_justification": "Evaluation based on available Matcher evidence."
    }

    class MockChain:
        def __or__(self, other):
            return self

        def invoke(self, inputs):
            return expected_evaluation


    class MockPrompt:
        def __or__(self, other):
            return MockChain()
    
    monkeypatch.setattr(
        ranker_nodes.ChatPromptTemplate,
        "from_messages",
        lambda messages: MockPrompt()
    )

    state = {
        "incoming_candidate": {
            "id": "candidate_x"
        },
        "match_result": {
            "candidate_id": "candidate_x",
            "overall_score": 80,
            "match_scores": {}
        },
        "secondary_rubric": {
            "criteria": {
                "relevant_experience": {},
                "project_impact": {},
                "problem_solving": {}
            }
        },
        "errors": []
    }

    result = ranker_nodes.evaluate_secondary_metrics(state)

    assert result["secondary_evaluation"] == expected_evaluation
    assert result["errors"] == []



def test_evaluate_secondary_metrics_rejects_invalid_insufficient_score(monkeypatch):

    import agents.ranker.nodes as ranker_nodes

    invalid_evaluation = {
        "criteria_scores": {
            "relevant_experience": {
                "score": 80,
                "evidence_status": "sufficient",
                "justification": "Relevant experience found."
            },
            "project_impact": {
                "score": 75,
                "evidence_status": "partial",
                "justification": "Some project impact evidence found."
            },
            "problem_solving": {
                "score": 30,
                "evidence_status": "insufficient",
                "justification": "Insufficient evidence available."
            }
        },
        "overall_justification": "Evaluation based on available evidence."
    }

    class MockChain:
        def __or__(self, other):
            return self

        def invoke(self, inputs):
            return invalid_evaluation

    class MockPrompt:
        def __or__(self, other):
            return MockChain()

    monkeypatch.setattr(
        ranker_nodes.ChatPromptTemplate,
        "from_messages",
        lambda messages: MockPrompt()
    )

    state = {
        "incoming_candidate": {
            "id": "candidate_x"
        },
        "match_result": {
            "candidate_id": "candidate_x",
            "overall_score": 80,
            "match_scores": {}
        },
        "secondary_rubric": {
            "criteria": {
                "relevant_experience": {},
                "project_impact": {},
                "problem_solving": {}
            }
        },
        "errors": []
    }

    result = ranker_nodes.evaluate_secondary_metrics(state)

    assert "secondary_evaluation" not in result
    assert len(result["errors"]) == 1
    assert result["errors"][0]["error_type"] == "invalid_insufficient_score"
    assert result["errors"][0]["retryable"] is True




def test_calculate_secondary_score_handles_boundary_scores():

    state = {
        "secondary_rubric": {
            "criteria": {
                "experience": {"weight": 0.5},
                "projects": {"weight": 0.5}
            }
        },
        "secondary_evaluation": {
            "criteria_scores": {
                "experience": {
                    "score": 0,
                    "evidence_status": "sufficient",
                    "justification": "No relevant experience."
                },
                "projects": {
                    "score": 100,
                    "evidence_status": "sufficient",
                    "justification": "Excellent project evidence."
                }
            },
            "overall_justification": "Evaluation completed."
        },
        "errors": []
    }

    result = calculate_secondary_score(state)

    assert result["secondary_evaluation"]["weighted_score"] == 50.0
    assert result["errors"] == []







def test_rank_candidates_sorts_and_assigns_competition_ranks():
    from agents.ranker.nodes import rank_candidates

    state = {
        "existing_candidates": [
            {
                "candidate_id": "candidate_A",
                "overall_score": 95,
                "match_scores": {},
                "secondary_score": 80,
                "secondary_details": {},
                "rank": 0,
                "one_line_rationale": "Strong candidate."
            },
            {
                "candidate_id": "candidate_B",
                "overall_score": 92,
                "match_scores": {},
                "secondary_score": 90,
                "secondary_details": {},
                "rank": 0,
                "one_line_rationale": "Good candidate."
            },
            {
                "candidate_id": "candidate_C",
                "overall_score": 92,
                "match_scores": {},
                "secondary_score": 90,
                "secondary_details": {},
                "rank": 0,
                "one_line_rationale": "Good candidate."
            },
            {
                "candidate_id": "candidate_D",
                "overall_score": 92,
                "match_scores": {},
                "secondary_score": 75,
                "secondary_details": {},
                "rank": 0,
                "one_line_rationale": "Average candidate."
            }
        ],
        "incoming_candidate": {
            "id": "candidate_E",
            "name": "Candidate E"
        },
        "match_result": {
            "candidate_id": "candidate_E",
            "overall_score": 87,
            "match_scores": {}
        },
        "secondary_evaluation": {
            "weighted_score": 95,
            "criteria_scores": {},
            "overall_justification": "Excellent secondary evaluation."
        },
        "errors": []
    }

    result = rank_candidates(state)

    ranked = result["ranked_candidates"]

    assert [
        candidate["candidate_id"] for candidate in ranked
    ] == [
        "candidate_A",
        "candidate_B",
        "candidate_C",
        "candidate_D",
        "candidate_E"
    ]

    assert [
        candidate["rank"] for candidate in ranked
    ] == [1, 2, 2, 4, 5]





def test_rank_candidates_updates_existing_candidate():
    from agents.ranker.nodes import rank_candidates

    existing_candidate = {
        "candidate_id": "candidate_A",
        "overall_score": 80,
        "match_scores": {"old": "data"},
        "secondary_score": 70,
        "secondary_details": {},
        "rank": 2,
        "one_line_rationale": "Old evaluation."
    }

    state = {
        "existing_candidates": [existing_candidate],
        "incoming_candidate": {
            "id": "candidate_A",
            "name": "Candidate A"
        },
        "match_result": {
            "candidate_id": "candidate_A",
            "overall_score": 95,
            "match_scores": {"new": "data"}
        },
        "secondary_evaluation": {
            "weighted_score": 90,
            "criteria_scores": {},
            "overall_justification": "Updated evaluation."
        },
        "errors": []
    }

    result = rank_candidates(state)

    ranked = result["ranked_candidates"]

    assert len(ranked) == 1

    assert ranked[0]["candidate_id"] == "candidate_A"
    assert ranked[0]["overall_score"] == 95
    assert ranked[0]["secondary_score"] == 90
    assert ranked[0]["match_scores"] == {"new": "data"}
    assert ranked[0]["one_line_rationale"] == "Updated evaluation."
    assert ranked[0]["rank"] == 1







def test_persist_rankings_creates_new_records(
    db_setup,
    rubric_job
):
    candidate = Candidate(
        name="Test Candidate",
        email="test@example.com",
        mobile_number="9876543210",
        linkedin_url="https://linkedin.com/in/test",
        google_form_response_id="test-form-response-001"
    )

    db_setup.add(candidate)
    db_setup.commit()

    state = {
        "jd_id": rubric_job.id,
        "ranked_candidates": [
            {
                "candidate_id": candidate.id,
                "overall_score": 90,
                "match_scores": {"technical_skills": {"score": 95}},
                "secondary_score": 85,
                "secondary_details": {
                    "criteria_scores": {},
                    "weighted_score": 85
                },
                "rank": 1,
                "one_line_rationale": "Strong technical candidate."
            }
        ],
        "errors": []
    }

    result = persist_rankings(state)

    assert result["errors"] == []

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
    assert saved_record.secondary_score == 85
    assert saved_record.rank == 1
    assert saved_record.one_line_rationale == "Strong technical candidate."




def test_persist_rankings_updates_existing_records(db_setup, rubric_job):
    candidate = Candidate(
        name="Test Candidate",
        email="test@example.com",
        mobile_number="9876543210",
        google_form_response_id="test-form-response-002"
    )

    db_setup.add(candidate)
    db_setup.commit()

    existing_record = CandidateRanking(
        jd_id=rubric_job.id,
        candidate_id=candidate.id,
        overall_score=80,
        match_scores={"technical_skills": {"score": 80}},
        secondary_score=75,
        secondary_details={
            "criteria_scores": {},
            "weighted_score": 75
        },
        rank=2,
        one_line_rationale="Good candidate."
    )

    db_setup.add(existing_record)
    db_setup.commit()

    state = {
        "jd_id": rubric_job.id,
        "ranked_candidates": [
            {
                "candidate_id": candidate.id,
                "overall_score": 95,
                "match_scores": {"technical_skills": {"score": 95}},
                "secondary_score": 90,
                "secondary_details": {
                    "criteria_scores": {},
                    "weighted_score": 90
                },
                "rank": 1,
                "one_line_rationale": "Excellent candidate."
            }
        ],
        "errors": []
    }

    result = persist_rankings(state)

    assert result["errors"] == []

    records = (
        db_setup.query(CandidateRanking)
        .filter(
            CandidateRanking.jd_id == rubric_job.id,
            CandidateRanking.candidate_id == candidate.id
        )
        .all()
    )

    assert len(records) == 1
    assert records[0].overall_score == 95
    assert records[0].secondary_score == 90
    assert records[0].rank == 1
    assert records[0].one_line_rationale == "Excellent candidate."




def test_load_existing_rankings(db_setup, rubric_job):
    candidate = Candidate(
        name="Test Candidate",
        email="test@example.com",
        mobile_number="9876543210",
        google_form_response_id="load-ranking-test-001"
    )

    db_setup.add(candidate)
    db_setup.commit()

    ranking = CandidateRanking(
        jd_id=rubric_job.id,
        candidate_id=candidate.id,
        overall_score=90,
        match_scores={"technical_skills": {"score": 95}},
        secondary_score=85,
        secondary_details={
            "criteria_scores": {},
            "weighted_score": 85
        },
        rank=1,
        one_line_rationale="Strong technical candidate."
    )

    db_setup.add(ranking)
    db_setup.commit()

    result = load_existing_rankings({
        "jd_id": rubric_job.id,
        "errors": []
    })

    assert result["errors"] == []
    assert len(result["existing_candidates"]) == 1

    loaded = result["existing_candidates"][0]

    assert loaded["candidate_id"] == candidate.id
    assert loaded["overall_score"] == 90
    assert loaded["secondary_score"] == 85
    assert loaded["rank"] == 1



def test_load_existing_rankings_returns_empty_list(db_setup, rubric_job):
    result = load_existing_rankings({
        "jd_id": rubric_job.id,
        "errors": []
    })

    assert result["errors"] == []
    assert result["existing_candidates"] == []
