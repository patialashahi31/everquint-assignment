from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.schemas.booking import BookingCreate, BookingResponse, BookingListResponse
from app.schemas.error import ErrorResponse
from app.services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "",
    response_model=BookingResponse,
    status_code=201,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error (e.g. start >= end, past time, duration > 2h)"},
        404: {"model": ErrorResponse, "description": "Room not found"},
        409: {"model": ErrorResponse, "description": "Room is already booked for the requested time slot"},
    },
)
def create_booking(
    payload: BookingCreate,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
):
    return BookingService(db).create_booking(payload, idempotency_key=idempotency_key)


@router.get(
    "",
    response_model=BookingListResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
    },
)
def list_bookings(
    roomId: Optional[str] = Query(None),
    from_time: Optional[datetime] = Query(None, alias="from"),
    to_time: Optional[datetime] = Query(None, alias="to"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return BookingService(db).list_bookings(
        room_id=roomId,
        from_time=from_time,
        to_time=to_time,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/{booking_id}/cancel",
    response_model=BookingResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Booking not found"},
        409: {"model": ErrorResponse, "description": "Booking is already cancelled"},
    },
)
def cancel_booking(
    booking_id: str,
    db: Session = Depends(get_db),
):
    return BookingService(db).cancel_booking(booking_id)