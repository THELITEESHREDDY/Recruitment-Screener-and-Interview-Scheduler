from datetime import date, time
from typing import Literal
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


class WorkingHours(BaseModel):
    start_time: str
    end_time: str


class InterviewWindow(WorkingHours):
    date: str


class SchedulingRequest(BaseModel):
    mode: Literal["explicit", "automatic"]
    top_n: int = Field(default=3, ge=1)
    interview_duration_minutes: int = Field(ge=1)

    schedule: list[InterviewWindow] | None = None
    start_date: str | None = None
    daily_working_hours: WorkingHours | None = None

    @model_validator(mode="after")
    def validate_mode_fields(self):
        if self.mode == "explicit":
            if not self.schedule:
                raise ValueError(
                    "Explicit scheduling requires schedule"
                )
        else:
            if not self.start_date or not self.daily_working_hours:
                raise ValueError(
                    "Automatic scheduling requires start_date "
                    "and daily_working_hours"
                )

        return self