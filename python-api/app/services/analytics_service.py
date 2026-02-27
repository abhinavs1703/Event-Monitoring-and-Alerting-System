from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.alert import AlertIncident
from app.models.event import Event


class AnalyticsService:
    def summary(self, db: Session) -> dict:
        total_events = db.scalar(select(func.count(Event.id))) or 0
        total_alerts = db.scalar(select(func.count(AlertIncident.id))) or 0
        latest_event = db.scalar(select(func.max(Event.timestamp)))
        return {
            "total_events": total_events,
            "total_alerts": total_alerts,
            "latest_event_timestamp": latest_event,
        }

    def severity_distribution(self, db: Session) -> list[dict]:
        rows = db.execute(select(Event.severity, func.count(Event.id)).group_by(Event.severity)).all()
        return [{"severity": severity, "count": count} for severity, count in rows]

    def time_series(self, db: Session) -> list[dict]:
        rows = db.execute(
            select(func.date_trunc("minute", Event.timestamp), func.count(Event.id))
            .group_by(func.date_trunc("minute", Event.timestamp))
            .order_by(func.date_trunc("minute", Event.timestamp))
        ).all()
        return [{"minute": str(minute), "count": count} for minute, count in rows]
