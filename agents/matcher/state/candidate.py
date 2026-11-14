from typing import TypedDict


class CandidateState(TypedDict):
    id: str
    name: str
    mobile_number: str
    email: str
    linkedin_url: str

    technical_skills: list[str]
    soft_skills: list[str]
    tech_stacks: list[str]
    tools_and_platforms: list[str]
    certifications: list[str]
    work_experience: list[str]
    coursework: list[str]
    achievements: list[str]
    education: str

    PEP_score: int
    PEP_priority: int