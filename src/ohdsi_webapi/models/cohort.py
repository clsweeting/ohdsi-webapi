from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, field_validator


class CohortDefinition(BaseModel):
    id: int | None = None
    name: str
    description: str | None = None
    expressionType: str = "SIMPLE_EXPRESSION"
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
    sourceKey: str


class JobStatus(BaseModel):
    executionId: int | None = None
    status: str
    startTime: str | None = None
    endTime: str | None = None


class InclusionRuleStats(BaseModel):
    id: int
    name: str
    count: int
    personCount: int


class CohortCount(BaseModel):
    cohortDefinitionId: int
    subjectCount: int
    entryCount: int
