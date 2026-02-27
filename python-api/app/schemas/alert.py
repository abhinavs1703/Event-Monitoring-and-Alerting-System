from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AlertRuleCreate(BaseModel):
    name: str = Field(min_length=3)
    event_type: str
    severity: str
    threshold_count: int = Field(ge=1)
    window_seconds: int = Field(ge=1)
    enabled: bool = True


class AlertRuleUpdate(BaseModel):
    event_type: str | None = None
    severity: str | None = None
    threshold_count: int | None = Field(default=None, ge=1)
    window_seconds: int | None = Field(default=None, ge=1)
    enabled: bool | None = None


class AlertRuleOut(AlertRuleCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class AlertIncidentOut(BaseModel):
    id: UUID
    rule_id: UUID
    severity: str
    summary: str
    incident_metadata: dict
    triggered_at: datetime

    class Config:
        from_attributes = True
