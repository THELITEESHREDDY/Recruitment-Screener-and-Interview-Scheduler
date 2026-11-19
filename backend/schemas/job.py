from pydantic import BaseModel, ConfigDict, Field

class JobCreate(BaseModel):
    job_description: str = Field(min_length=1)

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_description: str