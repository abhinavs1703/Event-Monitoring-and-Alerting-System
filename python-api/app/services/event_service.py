from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.event import Event
from app.schemas.event import EventIn
from app.services.alert_engine import AlertEngine


class EventService:
    def __init__(self) -> None:
        self.alert_engine = AlertEngine()

    def ingest_event(self, db: Session, payload: EventIn) -> Event:
        event = Event(**payload.model_dump())
        db.add(event)
        db.flush()
        self.alert_engine.evaluate(db, payload)
        db.commit()
        db.refresh(event)
        return event

    def list_events(self, db: Session, offset: int, limit: int, severity: str | None, source_id: str | None) -> list[Event]:
        query: Select[tuple[Event]] = select(Event).order_by(Event.timestamp.desc())
        if severity:
            query = query.where(Event.severity == severity)
        if source_id:
            query = query.where(Event.source_id == source_id)
        return db.scalars(query.offset(offset).limit(limit)).all()

    def get_event(self, db: Session, event_id: UUID) -> Event | None:
        return db.scalar(select(Event).where(Event.id == event_id))

    def get_by_source(self, db: Session, source_id: str, limit: int = 100) -> list[Event]:
        return db.scalars(select(Event).where(Event.source_id == source_id).limit(limit)).all()
