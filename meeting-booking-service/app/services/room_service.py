from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.room import Room
from app.schemas.room import RoomCreate
from app.exceptions import ConflictError, NotFoundError


class RoomService:
    def __init__(self, db: Session):
        self.db = db

    def create_room(self, payload: RoomCreate) -> Room:
        # Case-insensitive uniqueness check
        existing = (
            self.db.query(Room)
            .filter(func.lower(Room.name) == payload.name.lower())
            .first()
        )
        if existing:
            raise ConflictError(f"Room with name '{payload.name}' already exists")

        room = Room(
            name=payload.name,
            capacity=payload.capacity,
            floor=payload.floor,
            amenities=payload.amenities,
        )
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        return room

    def list_rooms(
        self,
        min_capacity: int | None = None,
        amenity: str | None = None,
    ) -> list[Room]:
        query = self.db.query(Room)

        if min_capacity is not None:
            query = query.filter(Room.capacity >= min_capacity)

        if amenity is not None:
            query = query.filter(Room.amenities.any(amenity))

        return query.all()

    def get_room_or_404(self, room_id: str) -> Room:
        room = self.db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise NotFoundError(f"Room with id '{room_id}' not found")
        return room