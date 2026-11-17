import math
from pydantic import BaseModel, Field, field_validator
from typing import Literal




class SecondaryCriterionOutput(BaseModel):
    weight: float = Field(ge=0)
    description: str = Field(min_length=1)
    evaluation_guidelines: list[str] = Field(min_length=1)

    @field_validator("weight")
    @classmethod
    def validate_finite_weight(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("Weight must be a finite number.")
        return value


class SecondaryRubricOutput(BaseModel):
    criteria: dict[str, SecondaryCriterionOutput]


class CriterionEvaluation(BaseModel):
    score: float = Field(ge=0, le=100)

    evidence_status: Literal[
        "sufficient",
        "partial",
        "insufficient",
        "contradictory"
    ]

    justification: str = Field(min_length=1)

class SecondaryEvaluationOutput(BaseModel):
    criteria_scores: dict[str, CriterionEvaluation] = Field(min_length=1)
    overall_justification: str = Field(min_length=1)