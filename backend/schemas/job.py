from pydantic import BaseModel, ConfigDict, Field

class JobCreate(BaseModel):
    job_description: str = Field(min_length=1)
    spreadsheet_url: str = Field(
        max_length=2048
    )

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_description: str
    spreadsheet_url: str | None = None