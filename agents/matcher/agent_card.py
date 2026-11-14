from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

matcher_skill = AgentSkill(
    id="candidate-matching",
    name="Candidate Matching",
    description=(
        "Evaluates candidate profiles against job descriptions "
        "using an Ideal Candidate profile. Generates section-wise "
        "scores, justifications, matched items, missing requirements, "
        "and an overall weighted match score."
    ),
    tags=[
        "recruitment",
        "candidate-evaluation",
        "resume-screening",
        "candidate-matching",
    ],
    examples=[
        "Evaluate a candidate against a given job description.",
        "Calculate a candidate's overall match score.",
    ],
)

ideal_candidate_skill = AgentSkill(
    id="ideal-candidate-generation",
    name="Ideal Candidate Generation",
    description=(
        "Generates an Ideal Candidate profile from a job description, "
        "including technical skills, soft skills, experience, education, "
        "mandatory requirements, preferred requirements, and evaluation weights."
    ),
    tags=[
        "job-description-analysis",
        "ideal-candidate",
        "requirements-extraction",
    ],
    examples=[
        "Generate an Ideal Candidate profile from a job description."
    ],
)

matcher_capabilities = AgentCapabilities(
    streaming=False,
    push_notifications=False,
)

matcher_agent_card = AgentCard(
    name="Recruitment Matcher Agent",
    description=(
        "An AI-powered recruitment evaluation agent that matches "
        "candidate profiles against job descriptions. It generates "
        "and persists Ideal Candidate profiles, calculates weighted "
        "match scores, validates results, and retries invalid outputs."
    ),
    url="http://localhost:8000/a2a/matcher",
    version="1.0.0",
    default_input_modes=["application/json"],
    default_output_modes=["application/json"],
    capabilities=matcher_capabilities,
    skills=[
        matcher_skill,
        ideal_candidate_skill,
    ],
)