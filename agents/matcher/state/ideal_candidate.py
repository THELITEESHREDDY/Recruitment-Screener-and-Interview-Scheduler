from typing import TypedDict


class IdealCandidate(TypedDict):
    technical_skills: list[str]
    soft_skills: list[str]
    tech_stacks: list[str]
    tools_and_platforms: list[str]
    certifications: list[str]
    work_experience: list[str]
    coursework: list[str]
    achievements: list[str]
    education: str

    mandatory_requirements: list[str]
    preferred_requirements: list[str]

    minimum_experience_years: float
    required_education_level: str

    evaluation_weights: dict[str, float]