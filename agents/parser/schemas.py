from pydantic import BaseModel
from typing import List

class get_contact_details_output(BaseModel):
    name:str
    mobile_number:str
    email:str
    linkedin_url:str



class get_skills_output(BaseModel):
    technical_skills: List[str]
    soft_skills: List[str]



class get_technical_skills_output(BaseModel):
    tech_stacks : List[str]
    tools_and_platforms: List[str]



class academic_skills_output(BaseModel):
  education: str
  coursework: str


class get_professional_details_output(BaseModel):
  work_experience: List[str]
  achievements: List[str]
  certifications: List[str]

