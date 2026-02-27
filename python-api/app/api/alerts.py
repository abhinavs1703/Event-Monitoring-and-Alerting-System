from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.alert import AlertRuleCreate, AlertRuleOut, AlertRuleUpdate
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])
service = AlertService()


@router.post("", response_model=AlertRuleOut, status_code=status.HTTP_201_CREATED)
def create_alert(payload: AlertRuleCreate, db: Session = Depends(get_db)):
    return service.create_rule(db, payload)


@router.get("", response_model=list[AlertRuleOut])
def list_alerts(db: Session = Depends(get_db)):
    return service.list_rules(db)


@router.put("/{rule_id}", response_model=AlertRuleOut)
def update_alert(rule_id: UUID, payload: AlertRuleUpdate, db: Session = Depends(get_db)):
    updated = service.update_rule(db, rule_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return updated


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(rule_id: UUID, db: Session = Depends(get_db)):
    ok = service.delete_rule(db, rule_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
