from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alert import AlertRule
from app.schemas.alert import AlertRuleCreate, AlertRuleUpdate


class AlertService:
    def create_rule(self, db: Session, payload: AlertRuleCreate) -> AlertRule:
        rule = AlertRule(**payload.model_dump())
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule

    def list_rules(self, db: Session) -> list[AlertRule]:
        return db.scalars(select(AlertRule).order_by(AlertRule.created_at.desc())).all()

    def update_rule(self, db: Session, rule_id: UUID, payload: AlertRuleUpdate) -> AlertRule | None:
        rule = db.scalar(select(AlertRule).where(AlertRule.id == rule_id))
        if not rule:
            return None

        for key, value in payload.model_dump(exclude_none=True).items():
            setattr(rule, key, value)

        db.commit()
        db.refresh(rule)
        return rule

    def delete_rule(self, db: Session, rule_id: UUID) -> bool:
        rule = db.scalar(select(AlertRule).where(AlertRule.id == rule_id))
        if not rule:
            return False
        db.delete(rule)
        db.commit()
        return True
