from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field, field_validator


class CohortDefinition(BaseModel):
    id: int | None = None
    name: str
    description: str | None = None
    expression_type: str = Field(default="SIMPLE_EXPRESSION", alias="expressionType")
    expression: dict[str, Any] | None = None

    @field_validator("expression", mode="before")
    @classmethod
    def parse_expression(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
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
