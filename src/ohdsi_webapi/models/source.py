from __future__ import annotations
from pydantic import BaseModel
from typing import Optional

class SourceDaimon(BaseModel):
    daimonType: str
    tableQualifier: Optional[str] = None
    priority: Optional[int] = None

class Source(BaseModel):
    sourceId: int
    sourceName: str
    sourceKey: str
    sourceDialect: str
    daimons: list[SourceDaimon] = []
