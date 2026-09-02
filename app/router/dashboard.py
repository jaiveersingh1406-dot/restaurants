from fastapi import APIRouter, HTTPException, Query

from app.service.dashboard import get_dashboard_stats

router = APIRouter()


@router.get("/dashboard/stats")
def dashboard_stats(
    period: str = Query("all", description="Filter: all | day | week | month"),
):
    try:
        return get_dashboard_stats(period=period)
    except HTTPException as exc:
        raise exc
