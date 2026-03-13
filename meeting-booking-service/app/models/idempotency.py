import uuid
from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
import enum
from app.models.base import Base


class IdempotencyStatus(str, enum.Enum):
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    idempotency_key: Mapped[str] = mapped_column(String, nullable=False)
    organizer_email: Mapped[str] = mapped_column(String, nullable=False)
    booking_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("bookings.id"), nullable=True
    )
    status: Mapped[IdempotencyStatus] = mapped_column(
        SAEnum(IdempotencyStatus), nullable=False, default=IdempotencyStatus.in_progress
    )
    response_body: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        # Unique per (key, organizer) — this is the concurrency guard
        __import__("sqlalchemy").UniqueConstraint(
            "idempotency_key", "organizer_email", name="uq_idempotency_key_organizer"
        ),
    )