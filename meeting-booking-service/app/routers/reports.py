from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.database import get_db
from app.schemas.report import RoomUtilizationReport
from app.schemas.error import ErrorResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "/room-utilization",
    response_model=List[RoomUtilizationReport],
    responses={
        400: {"model": ErrorResponse, "description": "Validation error (e.g. invalid date range)"},
    },
)
def room_utilization(
    from_time: datetime = Query(..., alias="from"),
    to_time: datetime = Query(..., alias="to"),
    db: Session = Depends(get_db),
):
    return ReportService(db).room_utilization(from_time=from_time, to_time=to_time)