
import json
import uuid

import pytest

from sqlalchemy.orm import sessionmaker

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from agents import pipeline
from agents.matcher import nodes as matcher_nodes
from agents.ranker import nodes as ranker_nodes
from agents.scheduler.tools.booking import booked_slots

from backend.models.job import JobDescription
from backend.models.ideal_candidate import IdealCandidateModel
from backend.models.candidate import Candidate
from backend.models.candidate_ranking import CandidateRanking


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


@pytest.mark.asyncio
async def test_complete_recruitment_pipeline(
    db_setup,
    monkeypatch
):
    # 1. Use the same isolated database for all agents.
    TestSessionLocal = sessionmaker(
        bind=db_setup.get_bind(),
        autoflush=False,
        autocommit=False
    )

    monkeypatch.setattr(
        pipeline, "LocalSession", TestSessionLocal
    )

    monkeypatch.setattr(
        matcher_nodes, "LocalSession", TestSessionLocal,
        raising=False
    )

    monkeypatch.setattr(
        ranker_nodes, "LocalSession", TestSessionLocal
    )

    booked_slots.clear()

    # 2. Create a Job Description.
    job = JobDescription(
        job_description="Python Backend Developer with FastAPI and SQL."
    )

    db_setup.add(job)
    db_setup.commit()
    db_setup.refresh(job)

    jd_id = job.id

    job_description = job.job_description

    # 3. Prepare the parsed candidate output.
    candidate_id = str(uuid.uuid4())

    parsed_candidate = {
        "id": candidate_id,
        "name": "Rahul Sharma",
        "mobile_number": "9876543210",
        "email": "rahul@example.com",
        "linkedin_url": "https://linkedin.com/in/rahul",
        "technical_skills": ["Python", "SQL", "FastAPI"],
        "soft_skills": ["Communication", "Problem Solving"],
        "tech_stacks": ["FastAPI", "PostgreSQL"],
        "technologies": ["Python"],
        "tools_and_platforms": ["Git", "Docker"],
        "certifications": [],
        "work_experience": ["1 year Python backend development"],
        "coursework": ["DBMS", "Operating Systems"],
        "achievements": ["Developed backend projects"],
        "education": "B.Tech Computer Science",
        "PEP_score": 80,
        "PEP_priority": 1
    }

    # 4. Mock Parser.
    async def mock_process_resume(
        pdf,
        candidate_id,
        pep_score,
        pep_priority
    ):
        return parsed_candidate

    monkeypatch.setattr(
        pipeline,
        "process_resume",
        mock_process_resume
    )

    # 5. Save an Ideal Candidate profile for Matcher.
    profile = {
        "technical_skills": ["Python", "SQL"],
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
            section: 100 / len(SECTIONS) 
            for section in SECTIONS
        }
    }

    db_setup.add(
        IdealCandidateModel(
            jd_id=jd_id,
            **profile
        )
    )
    db_setup.commit()

    # 6. Mock Matcher LLM response.
    match_scores = {
        section: {
            "score": 80.0,
            "justification": f"Evidence supports {section}.",
            "matched_items": ["Python"],
            "missing_items": [],
            "evidence": ["Candidate profile"]
        }
        for section in SECTIONS
    }

    monkeypatch.setattr(
        matcher_nodes,
        "llm_service",
        RunnableLambda(
            lambda messages: AIMessage(
                content=json.dumps(match_scores)
            )
        )
    )

    # 7. Mock Ranker rubric generation.
    rubric = {
        "criteria": {
            "relevant_experience": {
                "weight": 0.4,
                "description": "Relevant backend experience.",
                "evaluation_guidelines": ["Assess experience."]
            },
            "project_impact": {
                "weight": 0.35,
                "description": "Project impact.",
                "evaluation_guidelines": ["Assess outcomes."]
            },
            "problem_solving": {
                "weight": 0.25,
                "description": "Problem-solving ability.",
                "evaluation_guidelines": ["Assess problem solving."]
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

    # 8. Mock Ranker evaluation.
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
        "overall_justification": "Strong candidate."
    }

    class MockChain:
        def __or__(self, other):
            return self

        def invoke(self, inputs):
            return evaluation

    class MockPrompt:
        def __or__(self, other):
            return MockChain()

    class MockChatPromptTemplate:
        @staticmethod
        def from_messages(messages):
            return MockPrompt()


    monkeypatch.setattr(
        ranker_nodes,
        "ChatPromptTemplate",
        MockChatPromptTemplate
    )

    # 9. Execute the complete pipeline.
    result = await pipeline.run_recruitment_pipeline(
        jd_id=jd_id,
        job_description=job_description,
        candidates=[
            {
                "candidate_id": candidate_id,
                "pdf": None,
                "pep_score": 80,
                "pep_priority": 1
            }
        ],
        top_n=1
    )

    # 10. Verify candidate persistence.
    saved_candidate = db_setup.query(Candidate).filter(
        Candidate.id == candidate_id
    ).first()

    assert saved_candidate is not None
    assert saved_candidate.email == "rahul@example.com"
    print("\nPIPELINE CANDIDATE ERRORS:")
    print(result["candidate_errors"])

    # 11. Verify ranking.
    assert len(result["ranked_candidates"]) == 1

    ranked_candidate = result["ranked_candidates"][0]

    assert ranked_candidate["candidate_id"] == candidate_id
    assert ranked_candidate["rank"] == 1

    saved_ranking = db_setup.query(CandidateRanking).filter(
        CandidateRanking.jd_id == jd_id,
        CandidateRanking.candidate_id == candidate_id
    ).first()

    assert saved_ranking is not None

    # 12. Verify scheduling.


    assert result["candidate_errors"] == []
    # Verify pipeline response
    assert "ranked_candidates" in result
    assert "candidate_errors" in result

    # Screening no longer performs scheduling
    assert "schedule" not in result
    assert "scheduler_errors" not in result

    # Verify successful ranking
    assert result["candidate_errors"] == []
    assert len(result["ranked_candidates"]) == 1

    ranked_candidate = result["ranked_candidates"][0]

    assert ranked_candidate["candidate_id"] == candidate_id
    assert ranked_candidate["rank"] == 1

    # Verify ranking persistence
    saved_ranking = db_setup.query(CandidateRanking).filter(
        CandidateRanking.jd_id == jd_id,
        CandidateRanking.candidate_id == candidate_id
    ).first()

    assert saved_ranking is not None
    assert saved_ranking.rank == 1