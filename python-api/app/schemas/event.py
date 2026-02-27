from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class EventIn(BaseModel):
    event_id: UUID
    source_id: str = Field(min_length=3, max_length=100)
    timestamp: datetime
    severity: str
    event_type: str
    payload: dict[str, Any]


class EventOut(EventIn):
    id: UUID

    class Config:
        from_attributes = True
