from typing import TypedDict, Literal, List, Annotated
from operator import or_


class PdfDocument(TypedDict):
    filename: str
    content_type: Literal["application/pdf"]
    data: bytes


class InputState(TypedDict):
    candidate_resume: PdfDocument
    candidate_id: str
    resume_content: List[str]
    pep_score:int
    pep_priority:int


class OutputState(TypedDict):
    id: str
    name: str
    mobile_number: str
    email: str
    linkedin_url: str|None

    technical_skills: List[str]
    soft_skills: List[str]

    tech_stacks: List[str]
    technologies: List[str]
    tools_and_platforms: List[str]

    certifications: List[str]
    work_experience: List[str]
    coursework: List[str]
    achievements: List[str]

    education: str

    PEP_score: int
    PEP_priority: int


# Allows individual nodes to return partial output updates.
class PartialOutputState(TypedDict, total=False):
    id: str
    name: str
    mobile_number: str
    email: str
    linkedin_url: str|None

    technical_skills: List[str]
    soft_skills: List[str]

    tech_stacks: List[str]
    technologies: List[str]
    tools_and_platforms: List[str]

    certifications: List[str] 
    work_experience: List[str]  
    coursework: List[str] 
    achievements: List[str] 

    education: str

    PEP_score: int
    PEP_priority: int


class OverallState(TypedDict):
    id: str
    user_input: InputState

    graph_output: Annotated[
        PartialOutputState,
        or_
    ]
