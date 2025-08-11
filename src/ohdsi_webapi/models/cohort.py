from __future__ import annotations

import json

from ohdsi_cohort_schemas import CohortExpression
from pydantic import BaseModel, Field, field_validator


class CohortDefinition(BaseModel):
    id: int | None = None
    name: str
    description: str | None = None
    expression_type: str = Field(default="SIMPLE_EXPRESSION", alias="expressionType")
    expression: CohortExpression | None = None

    @field_validator("expression", mode="before")
    @classmethod
    def parse_expression(cls, v):
        if isinstance(v, str):
            try:
                data = json.loads(v)
                return CohortExpression.model_validate(data)
            except (json.JSONDecodeError, ValueError):
                return None
        elif isinstance(v, dict):
            try:
                return CohortExpression.model_validate(v)
            except ValueError:
                return None
        return v


class CohortGenerationRequest(BaseModel):
    # structure may include various settings; keep flexible
    id: int
    source_key: str = Field(alias="sourceKey")


class JobStatus(BaseModel):
    execution_id: int | None = Field(default=None, alias="executionId")
    status: str
    start_time: str | None = Field(default=None, alias="startTime")
    end_time: str | None = Field(default=None, alias="endTime")


class InclusionRuleStats(BaseModel):
    id: int
    name: str
    count: int
    person_count: int = Field(alias="personCount")


class CohortCount(BaseModel):
    cohort_definition_id: int = Field(alias="cohortDefinitionId")
    subject_count: int = Field(alias="subjectCount")
    entry_count: int = Field(alias="entryCount")
