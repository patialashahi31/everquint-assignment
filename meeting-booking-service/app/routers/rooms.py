from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.room import RoomCreate, RoomResponse
from app.schemas.error import ErrorResponse
from app.services.room_service import RoomService

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.post(
    "",
    response_model=RoomResponse,
    status_code=201,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        409: {"model": ErrorResponse, "description": "Room with this name already exists"},
    },
)
def create_room(
    payload: RoomCreate,
    db: Session = Depends(get_db),
):
    return RoomService(db).create_room(payload)


@router.get("", response_model=List[RoomResponse])
def list_rooms(
    minCapacity: Optional[int] = Query(None, ge=1),
    amenity: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return RoomService(db).list_rooms(min_capacity=minCapacity, amenity=amenity)