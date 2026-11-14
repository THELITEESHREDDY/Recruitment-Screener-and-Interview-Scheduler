from pydantic import BaseModel

class IdealCandidate(BaseModel):
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




class SectionMatch(BaseModel):
    score: float
    justification: str
    matched_items: list[str]
    missing_items: list[str]
    evidence: list[str]




class MatchScores(BaseModel):
    technical_skills: SectionMatch
    soft_skills: SectionMatch
    tech_stacks: SectionMatch
    tools_and_platforms: SectionMatch
    certifications: SectionMatch
    work_experience: SectionMatch
    coursework: SectionMatch
    achievements: SectionMatch
    education: SectionMatch






class MatchResult(BaseModel):
    candidate_id: str

    match_scores: MatchScores
    overall_score: float
    eligibility_status: str
    recommendation: str
    recommendation_reason: str