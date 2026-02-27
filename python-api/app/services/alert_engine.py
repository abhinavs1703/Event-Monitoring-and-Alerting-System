from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.alert import AlertIncident, AlertRule
from app.models.event import Event
from app.schemas.event import EventIn


class AlertEngine:
    def evaluate(self, db: Session, event: EventIn) -> list[AlertIncident]:
        rules = db.scalars(
            select(AlertRule).where(
                AlertRule.enabled.is_(True),
                AlertRule.event_type == event.event_type,
                AlertRule.severity == event.severity,
            )
        ).all()

        incidents: list[AlertIncident] = []
        for rule in rules:
            window_start = event.timestamp - timedelta(seconds=rule.window_seconds)
            count_query = select(func.count(Event.id)).where(
                Event.event_type == event.event_type,
                Event.severity == event.severity,
                Event.timestamp >= window_start,
            )
            count = db.scalar(count_query) or 0
            if count >= rule.threshold_count:
                incident = AlertIncident(
                    rule_id=rule.id,
                    severity=rule.severity,
                    summary=f"Rule {rule.name} triggered for {event.event_type}",
                    incident_metadata={"observed_count": count, "window_seconds": rule.window_seconds},
                )
                db.add(incident)
                incidents.append(incident)

        return incidents
