import uuid
from sqlalchemy import String, Integer, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    floor: Mapped[int] = mapped_column(Integer, nullable=False)
    amenities: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)

    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="room")