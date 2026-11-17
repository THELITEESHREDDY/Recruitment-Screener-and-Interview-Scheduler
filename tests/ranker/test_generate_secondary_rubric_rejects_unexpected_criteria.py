
def test_generate_secondary_rubric_rejects_unexpected_criteria(monkeypatch):
    import agents.ranker.nodes as ranker_nodes

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
