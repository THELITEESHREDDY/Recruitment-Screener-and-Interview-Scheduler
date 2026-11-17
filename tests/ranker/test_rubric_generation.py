import agents.ranker.nodes as ranker_nodes


def test_generate_secondary_rubric_rejects_zero_total_weight(monkeypatch):
    

    class MockChain:
        def invoke(self, inputs):
            return {
                "criteria": {
                    "relevant_experience": {
                        "weight": 0.4,
                        "description": "Experience",
                        "evaluation_guidelines": ["Assess experience."]
                    },
                    "project_impact": {
                        "weight": 0.3,
                        "description": "Project impact",
                        "evaluation_guidelines": ["Assess impact."]
                    },
                    "communication": {
                        "weight": 0.3,
                        "description": "Communication",
                        "evaluation_guidelines": ["Assess communication."]
                    }
                }
            }

    monkeypatch.setattr(
        ranker_nodes,
        "llm_service",
        lambda *args, **kwargs: None
    )

    # Replace the chain construction so no real LLM call occurs.
    monkeypatch.setattr(
        ranker_nodes,
        "ChatPromptTemplate",
        type(
            "MockPromptTemplate",
            (),
            {
                "from_messages": staticmethod(
                    lambda messages: type(
                        "MockPrompt",
                        (),
                        {
                            "__or__": lambda self, other: type(
                                "MockParserChain",
                                (),
                                {
                                    "__or__": lambda self, parser: MockChain()
                                }
                            )()
                        }
                    )()
                )
            }
        )
    )

    result = ranker_nodes.generate_secondary_rubric({
        "jd_id": "test-jd",
        "job_description": "Backend developer",
        "errors": []
    })

    assert "secondary_rubric" not in result
    assert result["errors"][0]["error_type"] == "criteria_mismatch"
    assert result["errors"][0]["retryable"] is True


def test_generate_secondary_rubric_rejects_negative_weight(monkeypatch):    
    import agents.ranker.nodes as ranker_nodes

    class MockChain:
        def invoke(self, inputs):
            return {
                "criteria": {
                    "relevant_experience": {
                        "weight": -0.4,
                        "description": "Experience",
                        "evaluation_guidelines": ["Assess experience."]
                    },
                    "project_impact": {
                        "weight": 0.3,
                        "description": "Project impact",
                        "evaluation_guidelines": ["Assess impact."]
                    },
                    "problem_solving": {
                        "weight": 0.3,
                        "description": "Problem solving",
                        "evaluation_guidelines": ["Assess problem-solving skills."]
                    }                
                }
            }

    monkeypatch.setattr(
        ranker_nodes,
        "llm_service",
        lambda *args, **kwargs: None
    )

    # Replace the chain construction so no real LLM call occurs.
    monkeypatch.setattr(
        ranker_nodes,
        "ChatPromptTemplate",
        type(
            "MockPromptTemplate",
            (),
            {
                "from_messages": staticmethod(
                    lambda messages: type(
                        "MockPrompt",
                        (),
                        {
                            "__or__": lambda self, other: type(
                                "MockParserChain",
                                (),
                                {
                                    "__or__": lambda self, parser: MockChain()
                                }
                            )()
                        }
                    )()
                )
            }
        )
    )

    result = ranker_nodes.generate_secondary_rubric({
        "jd_id": "test-jd",
        "job_description": "Backend developer",
        "errors": []
    })

    assert "secondary_rubric" not in result
    assert result["errors"][0]["error_type"] == "ValidationError"
    assert result["errors"][0]["retryable"] is True



def test_generate_secondary_rubric_rejects_nan_weight(monkeypatch):    
    import agents.ranker.nodes as ranker_nodes

    class MockChain:
        def invoke(self, inputs):
            return {
                "criteria": {
                "relevant_experience": {
                "weight": float("nan"),
                "description": "Experience",
                "evaluation_guidelines": ["Assess experience."]
            },
            "project_impact": {
                "weight": 0.3,
                "description": "Project impact",
                "evaluation_guidelines": ["Assess impact."]
            },
            "problem_solving": {
                "weight": 0.7,
                "description": "Problem solving",
                "evaluation_guidelines": ["Assess problem solving."]
            }
        }
    }

    monkeypatch.setattr(
        ranker_nodes,
        "llm_service",
        lambda *args, **kwargs: None
    )

    # Replace the chain construction so no real LLM call occurs.
    monkeypatch.setattr(
        ranker_nodes,
        "ChatPromptTemplate",
        type(
            "MockPromptTemplate",
            (),
            {
                "from_messages": staticmethod(
                    lambda messages: type(
                        "MockPrompt",
                        (),
                        {
                            "__or__": lambda self, other: type(
                                "MockParserChain",
                                (),
                                {
                                    "__or__": lambda self, parser: MockChain()
                                }
                            )()
                        }
                    )()
                )
            }
        )
    )

    result = ranker_nodes.generate_secondary_rubric({
        "jd_id": "test-jd",
        "job_description": "Backend developer",
        "errors": []
    })

    assert "secondary_rubric" not in result
    assert result["errors"][0]["error_type"] == "ValidationError"
    assert result["errors"][0]["retryable"] is True


def test_generate_secondary_rubric_rejects_infinite_weight(monkeypatch):    
    import agents.ranker.nodes as ranker_nodes

    class MockChain:
        def invoke(self, inputs):
            return {
                "criteria": {
                "relevant_experience": {
                "weight": float("inf"),
                "description": "Experience",
                "evaluation_guidelines": ["Assess experience."]
            },
            "project_impact": {
                "weight": 0.3,
                "description": "Project impact",
                "evaluation_guidelines": ["Assess impact."]
            },
            "problem_solving": {
                "weight": 0.7,
                "description": "Problem solving",
                "evaluation_guidelines": ["Assess problem solving."]
            }
        }
    }

    monkeypatch.setattr(
        ranker_nodes,
        "llm_service",
        lambda *args, **kwargs: None
    )

    # Replace the chain construction so no real LLM call occurs.
    monkeypatch.setattr(
        ranker_nodes,
        "ChatPromptTemplate",
        type(
            "MockPromptTemplate",
            (),
            {
                "from_messages": staticmethod(
                    lambda messages: type(
                        "MockPrompt",
                        (),
                        {
                            "__or__": lambda self, other: type(
                                "MockParserChain",
                                (),
                                {
                                    "__or__": lambda self, parser: MockChain()
                                }
                            )()
                        }
                    )()
                )
            }
        )
    )

    result = ranker_nodes.generate_secondary_rubric({
        "jd_id": "test-jd",
        "job_description": "Backend developer",
        "errors": []
    })

    assert "secondary_rubric" not in result
    assert result["errors"][0]["error_type"] == "ValidationError"
    assert result["errors"][0]["retryable"] is True



def test_generate_secondary_rubric_normalizes_weights(monkeypatch):
    import agents.ranker.nodes as ranker_nodes

    class MockChain:
        def invoke(self, inputs):
            return {
                "criteria": {
                    "relevant_experience": {
                        "weight": 4,
                        "description": "Experience",
                        "evaluation_guidelines": ["Assess experience."]
                    },
                    "project_impact": {
                        "weight": 3,
                        "description": "Project impact",
                        "evaluation_guidelines": ["Assess impact."]
                    },
                    "problem_solving": {
                        "weight": 3,
                        "description": "Problem solving",
                        "evaluation_guidelines": ["Assess problem solving."]
                    }
                }
            }

    # Mock the LLM
    monkeypatch.setattr(
        ranker_nodes,
        "llm_service",
        lambda *args, **kwargs: None
    )

    # Mock prompt and chain construction
    monkeypatch.setattr(
        ranker_nodes,
        "ChatPromptTemplate",
        type(
            "MockPromptTemplate",
            (),
            {
                "from_messages": staticmethod(
                    lambda messages: type(
                        "MockPrompt",
                        (),
                        {
                            "__or__": lambda self, other: type(
                                "MockParserChain",
                                (),
                                {
                                    "__or__": lambda self, parser: MockChain()
                                }
                            )()
                        }
                    )()
                )
            }
        )
    )

    result = ranker_nodes.generate_secondary_rubric({
        "jd_id": "test-jd",
        "job_description": "Backend developer",
        "errors": []
    })

    # Verify successful generation
    assert "secondary_rubric" in result
    assert result["errors"] == []

    criteria = result["secondary_rubric"]["criteria"]

    # Verify normalized weights
    assert criteria["relevant_experience"]["weight"] == 0.4
    assert criteria["project_impact"]["weight"] == 0.3
    assert criteria["problem_solving"]["weight"] == 0.3

    # Verify total weight
    total_weight = sum(
        criterion["weight"] for criterion in criteria.values()
    )

    assert total_weight == 1.0



import pytest


def test_generate_secondary_rubric_normalizes_extreme_weights(monkeypatch):
    weights = {
        "relevant_experience": 0.0001,
        "project_impact": 1000000,
        "problem_solving": 0.0001
    }

    mock_response = {
        "criteria": {
            "relevant_experience": {
                "weight": weights["relevant_experience"],
                "description": "Relevant experience",
                "evaluation_guidelines": ["Check relevant experience"]
            },
            "project_impact": {
                "weight": weights["project_impact"],
                "description": "Project impact",
                "evaluation_guidelines": ["Check project impact"]
            },
            "problem_solving": {
                "weight": weights["problem_solving"],
                "description": "Problem solving",
                "evaluation_guidelines": ["Check problem solving"]
            }
        }
    }

    # Mock the LLM response
    class MockChain:
        def invoke(self, inputs):
            return mock_response

    monkeypatch.setattr(
        ranker_nodes,
        "llm_service",
        lambda *args, **kwargs: None
    )

    monkeypatch.setattr(
        ranker_nodes,
        "ChatPromptTemplate",
        type(
            "MockPromptTemplate",
            (),
            {
                "from_messages": staticmethod(
                    lambda messages: type(
                        "MockPrompt",
                        (),
                        {
                            "__or__": lambda self, other: type(
                                "MockParserChain",
                                (),
                                {
                                    "__or__": lambda self, parser: MockChain()
                                }
                            )()
                        }
                    )()
                )
            }
        )
    )

    result = ranker_nodes.generate_secondary_rubric({
        "jd_id": "test-jd",
        "job_description": "Backend developer",
        "errors": []
    })

    assert "secondary_rubric" in result
    assert result["errors"] == []

    normalized_weights = {
        name: criterion["weight"]
        for name, criterion in result["secondary_rubric"]["criteria"].items()
    }

    assert normalized_weights["relevant_experience"] == pytest.approx(0.0000000001)
    assert normalized_weights["project_impact"] == pytest.approx(0.9999999998)
    assert normalized_weights["problem_solving"] == pytest.approx(0.0000000001)

    assert sum(normalized_weights.values()) == pytest.approx(1.0)



def test_retrieve_rubric_with_missing_criteria_returns_error(db_setup):
    from backend.models.job import JobDescription
    from backend.models.job_ranking_rubrik import JobRankingRubric

    # Create a job description.
    job = JobDescription(
        job_description="Backend developer with Python and FastAPI experience."
    )

    db_setup.add(job)
    db_setup.commit()
    db_setup.refresh(job)

    # Insert an intentionally incomplete rubric.
    rubric = JobRankingRubric(
        jd_id=job.id,
        criteria={
            "relevant_experience": {
                "weight": 0.5,
                "description": "Relevant experience",
                "evaluation_guidelines": ["Check experience"]
            },
            "project_impact": {
                "weight": 0.5,
                "description": "Project impact",
                "evaluation_guidelines": ["Check impact"]
            }
        }
    )

    db_setup.add(rubric)
    db_setup.commit()

    result = ranker_nodes.get_or_create_secondary_rubric({
        "jd_id": job.id,
        "job_description": job.job_description,
        "errors": []
    })

    assert "secondary_rubric" not in result
    assert len(result["errors"]) == 1
    assert result["errors"][0]["error_type"] == "invalid_stored_rubric"
    assert result["errors"][0]["retryable"] is False




def test_retrieve_rubric_with_unexpected_criteria_returns_error(db_setup):
    from backend.models.job import JobDescription
    from backend.models.job_ranking_rubrik import JobRankingRubric

    # Create a job description.
    job = JobDescription(
        job_description="Backend developer with Python and FastAPI experience."
    )

    db_setup.add(job)
    db_setup.commit()
    db_setup.refresh(job)

    # Insert a rubric containing an unexpected criterion.
    rubric = JobRankingRubric(
        jd_id=job.id,
        criteria={
            "relevant_experience": {
                "weight": 0.4,
                "description": "Relevant experience",
                "evaluation_guidelines": ["Check experience"]
            },
            "project_impact": {
                "weight": 0.3,
                "description": "Project impact",
                "evaluation_guidelines": ["Check impact"]
            },
            "problem_solving": {
                "weight": 0.3,
                "description": "Problem solving",
                "evaluation_guidelines": ["Check problem solving"]
            },
            "communication": {
                "weight": 0.1,
                "description": "Communication",
                "evaluation_guidelines": ["Check communication"]
            }
        }
    )

    db_setup.add(rubric)
    db_setup.commit()

    result = ranker_nodes.get_or_create_secondary_rubric({
        "jd_id": job.id,
        "job_description": job.job_description,
        "errors": []
    })

    assert "secondary_rubric" not in result
    assert len(result["errors"]) == 1
    assert result["errors"][0]["error_type"] == "invalid_stored_rubric"
    assert result["errors"][0]["retryable"] is False