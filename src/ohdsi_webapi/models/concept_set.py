from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ConceptSet(BaseModel):
    id: int | None = None
    name: str
    oid: int | None = None
    tags: list[Any] | None = None
    expression: dict | None = None  # Raw expression


class ConceptSetExpression(BaseModel):
    items: list[dict]


class ConceptSetItem(BaseModel):
    """A concept set item as returned by /conceptset/{id}/items endpoint."""

    id: int
    conceptSetId: int
    conceptId: int
    isExcluded: int  # 0 or 1 in API
    includeDescendants: int  # 0 or 1 in API
    includeMapped: int | None = None  # 0 or 1 in API

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
    isExcluded: bool | None = None
    includeDescendants: bool | None = None
    includeMapped: bool | None = None
    # Additional fields may appear; store raw
    additionalFields: dict | None = None
