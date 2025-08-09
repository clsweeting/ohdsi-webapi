from __future__ import annotations
from pydantic import BaseModel
from typing import Optional

class Concept(BaseModel):
    conceptId: int
    conceptName: str
    vocabularyId: Optional[str] = None
    conceptClassId: Optional[str] = None
    standardConcept: Optional[str] = None
    conceptCode: Optional[str] = None
    domainId: Optional[str] = None
    validStartDate: Optional[str] = None
    validEndDate: Optional[str] = None
    invalidReason: Optional[str] = None

class ConceptAncestor(BaseModel):
    ancestorConceptId: int
    descendantConceptId: int
    minLevelsOfSeparation: Optional[int] = None
    maxLevelsOfSeparation: Optional[int] = None
