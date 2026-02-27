from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.event import EventIn, EventOut
from app.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["events"])
internal_router = APIRouter(prefix="/internal", tags=["internal"])
service = EventService()


@router.get("", response_model=list[EventOut])
def list_events(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    severity: str | None = None,
    source_id: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_events(db, offset, limit, severity, source_id)


@router.get("/{id}", response_model=EventOut)
def get_event(id: UUID, db: Session = Depends(get_db)):
    event = service.get_event(db, id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.get("/source/{source_id}", response_model=list[EventOut])
def get_events_by_source(source_id: str, db: Session = Depends(get_db)):
    return service.get_by_source(db, source_id)


@internal_router.post("/events", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def ingest_event(
    payload: EventIn,
    db: Session = Depends(get_db),
    x_ingest_token: str = Header(default=""),
):
    if x_ingest_token != settings.internal_ingest_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ingest token")

    try:
        return service.ingest_event(db, payload)
    except Exception as exc:  # structured boundary
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
