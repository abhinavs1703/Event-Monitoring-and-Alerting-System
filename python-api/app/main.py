from fastapi import FastAPI

from app.api.alerts import router as alerts_router
from app.api.analytics import router as analytics_router
from app.api.events import internal_router, router as events_router

app = FastAPI(title="Event Monitoring & Alerting API", version="1.0.0")

app.include_router(events_router)
app.include_router(alerts_router)
app.include_router(analytics_router)
app.include_router(internal_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
