import uuid
from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone  # ← add timezone here
import enum
from app.models.base import Base


class BookingStatus(str, enum.Enum):
    confirmed = "confirmed"
    cancelled = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    room_id: Mapped[str] = mapped_column(String, ForeignKey("rooms.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    organizer_email: Mapped[str] = mapped_column(String, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        SAEnum(BookingStatus), nullable=False, default=BookingStatus.confirmed
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    room: Mapped["Room"] = relationship("Room", back_populates="bookings")