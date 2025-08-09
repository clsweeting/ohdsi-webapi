from __future__ import annotations
from pydantic import BaseModel
from typing import Optional

class WebApiInfo(BaseModel):
    version: Optional[str] = None
    buildDate: Optional[str] = None
    gitCommitId: Optional[str] = None
