from __future__ import annotations

from pydantic import BaseModel


class SourceDaimon(BaseModel):
    daimonType: str
    tableQualifier: str | None = None
    priority: int | None = None


class Source(BaseModel):
    sourceId: int
    sourceName: str
    sourceKey: str
    sourceDialect: str
    daimons: list[SourceDaimon] = []
