from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, Any

class ConceptSet(BaseModel):
    id: int | None = None
    name: str
    oid: Optional[int] = None
    tags: Optional[list[Any]] = None
    expression: Optional[dict] = None  # Raw expression

class ConceptSetExpression(BaseModel):
    items: list[dict]

class ConceptSetItem(BaseModel):
    """A concept set item as returned by /conceptset/{id}/items endpoint."""
    id: int
    conceptSetId: int  
    conceptId: int
    isExcluded: int  # 0 or 1 in API
    includeDescendants: int  # 0 or 1 in API
    includeMapped: Optional[int] = None  # 0 or 1 in API
    
    @property
    def is_excluded(self) -> bool:
        """Convert isExcluded integer to boolean."""
        return bool(self.isExcluded)
    
    @property 
    def include_descendants(self) -> bool:
        """Convert includeDescendants integer to boolean."""
        return bool(self.includeDescendants)
    
    @property
    def include_mapped(self) -> bool:
        """Convert includeMapped integer to boolean."""
        return bool(self.includeMapped) if self.includeMapped is not None else False

class ResolvedConceptSetItem(BaseModel):
    """A resolved concept set item with concept details."""
    conceptId: int
    conceptName: str
    isExcluded: Optional[bool] = None
    includeDescendants: Optional[bool] = None
    includeMapped: Optional[bool] = None
    # Additional fields may appear; store raw
    additionalFields: dict | None = None
