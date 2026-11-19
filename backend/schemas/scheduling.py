from datetime import date, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, model_validator


class InterviewWindow(BaseModel):
    date: date
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def validate_window(self):
        if self.start_time >= self.end_time:
            raise ValueError(
                "start_time must be earlier than end_time"
            )

        return self


class InterviewerInput(BaseModel):
    name: str = Field(min_length=1)
    calendar_id: str = Field(min_length=1)


class SchedulingRequest(BaseModel):
    top_n: int = Field(default=3, ge=1)

    timezone: str = "Asia/Kolkata"

    interview_duration_minutes: int = Field(
        default=30,
        ge=15,
        le=120
    )

    schedule: list[InterviewWindow] = Field(min_length=1)

    interviewers: list[InterviewerInput] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_request(self):
        try:
            ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError:
            raise ValueError("Invalid timezone")

        return self