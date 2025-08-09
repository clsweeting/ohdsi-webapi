from __future__ import annotations

from pydantic import BaseModel


class Concept(BaseModel):
    conceptId: int
    conceptName: str
    vocabularyId: str | None = None
    conceptClassId: str | None = None
    standardConcept: str | None = None
    conceptCode: str | None = None
    domainId: str | None = None
    validStartDate: str | None = None
    validEndDate: str | None = None
    invalidReason: str | None = None


class ConceptAncestor(BaseModel):
    ancestorConceptId: int
    descendantConceptId: int
    minLevelsOfSeparation: int | None = None
    maxLevelsOfSeparation: int | None = None
