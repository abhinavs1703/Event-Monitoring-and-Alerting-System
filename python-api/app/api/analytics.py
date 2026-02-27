from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])
service = AnalyticsService()


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    return service.summary(db)


@router.get("/severity-distribution")
def severity_distribution(db: Session = Depends(get_db)):
    return service.severity_distribution(db)


@router.get("/time-series")
def time_series(db: Session = Depends(get_db)):
    return service.time_series(db)
