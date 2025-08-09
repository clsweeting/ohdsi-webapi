from __future__ import annotations

from pydantic import BaseModel


class WebApiInfo(BaseModel):
    version: str | None = None
    buildDate: str | None = None
    gitCommitId: str | None = None
