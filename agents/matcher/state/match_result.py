from typing import TypedDict


class SectionMatch(TypedDict):
    score: float
    justification: str
    matched_items: list[str]
    missing_items: list[str]
    evidence: list[str]


class MatchScores(TypedDict):
    technical_skills: SectionMatch
    soft_skills: SectionMatch
    tech_stacks: SectionMatch
    tools_and_platforms: SectionMatch
    certifications: SectionMatch
    work_experience: SectionMatch
    coursework: SectionMatch
    achievements: SectionMatch
    education: SectionMatch


class MatchResult(TypedDict):
    candidate_id: str

    match_scores: MatchScores

    overall_score: float