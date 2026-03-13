from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone, timedelta

from app.models.booking import Booking, BookingStatus
from app.models.idempotency import IdempotencyKey, IdempotencyStatus
from app.schemas.booking import BookingCreate, BookingListResponse, BookingResponse
from app.services.room_service import RoomService
from app.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)


BUSINESS_START_HOUR = 8
BUSINESS_END_HOUR = 20
BUSINESS_DAYS = {0, 1, 2, 3, 4}  # Mon–Fri


class BookingService:
    def __init__(self, db: Session):
        self.db = db

    # ── Public methods ───────────────────────────────────

    def create_booking(
        self,
        payload: BookingCreate,
        idempotency_key: str | None = None,
    ) -> Booking:
        # Resolve idempotency first — return cached if already completed
        if idempotency_key:
            cached = self._resolve_idempotency(idempotency_key, payload.organizerEmail)
            if cached:
                return cached

        # Validate room exists
        RoomService(self.db).get_room_or_404(payload.roomId)

        # Validate business rules
        self._validate_working_hours(payload.startTime, payload.endTime)
        self._validate_no_overlap(payload.roomId, payload.startTime, payload.endTime)

        booking = Booking(
            room_id=payload.roomId,
            title=payload.title,
            organizer_email=payload.organizerEmail,
            start_time=payload.startTime,
            end_time=payload.endTime,
            status=BookingStatus.confirmed,
        )
        self.db.add(booking)
        self.db.flush()  # assigns booking.id without committing

        if idempotency_key:
            self._save_idempotency_key(
                idempotency_key=idempotency_key,
                organizer_email=payload.organizerEmail,
                booking=booking,
            )

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError("Duplicate Idempotency-Key for this organizer")

        self.db.refresh(booking)
        return booking

    def list_bookings(
        self,
        room_id: str | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> BookingListResponse:
        query = self.db.query(Booking)

        if room_id:
            query = query.filter(Booking.room_id == room_id)
        if from_time:
            query = query.filter(Booking.end_time > from_time)
        if to_time:
            query = query.filter(Booking.start_time < to_time)

        total = query.count()
        items = query.order_by(Booking.start_time).offset(offset).limit(limit).all()

        return BookingListResponse(
            items=[BookingResponse.model_validate(b) for b in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    def cancel_booking(self, booking_id: str) -> Booking:
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise NotFoundError(f"Booking with id '{booking_id}' not found")

        # Already cancelled — no-op
        if booking.status == BookingStatus.cancelled:
            return booking

        # Grace period check — must cancel at least 1 hour before startTime
        now = datetime.now(timezone.utc)
        if (booking.start_time - now) < timedelta(hours=1):
            raise ValidationError(
                "Booking can only be cancelled at least 1 hour before start time"
            )

        booking.status = BookingStatus.cancelled
        self.db.commit()
        self.db.refresh(booking)
        return booking

    # ── Private helpers ──────────────────────────────────

    def _validate_working_hours(
        self, start_time: datetime, end_time: datetime
    ) -> None:
        start = start_time.astimezone(timezone.utc)
        end = end_time.astimezone(timezone.utc)

        if start.weekday() not in BUSINESS_DAYS:
            raise ValidationError("Bookings are only allowed Monday to Friday")

        if not (BUSINESS_START_HOUR <= start.hour < BUSINESS_END_HOUR):
            raise ValidationError(
                f"Bookings must start between {BUSINESS_START_HOUR}:00 and {BUSINESS_END_HOUR}:00"
            )

        if not (BUSINESS_START_HOUR <= end.hour <= BUSINESS_END_HOUR):
            raise ValidationError(
                f"Bookings must end by {BUSINESS_END_HOUR}:00"
            )

        if end.hour == BUSINESS_END_HOUR and end.minute > 0:
            raise ValidationError(
                f"Bookings must end by {BUSINESS_END_HOUR}:00"
            )

    def _validate_no_overlap(
        self, room_id: str, start_time: datetime, end_time: datetime
    ) -> None:
        # Lock room's bookings row to prevent concurrent overlapping inserts
        self.db.query(Booking).filter(
            Booking.room_id == room_id
        ).with_for_update().first()

        overlap = (
            self.db.query(Booking)
            .filter(
                Booking.room_id == room_id,
                Booking.status == BookingStatus.confirmed,
                Booking.start_time < end_time,
                Booking.end_time > start_time,
            )
            .first()
        )
        if overlap:
            raise ConflictError(
                f"Room is already booked from {overlap.start_time} to {overlap.end_time}"
            )

    def _resolve_idempotency(
        self, idempotency_key: str, organizer_email: str
    ) -> Booking | None:
        existing = (
            self.db.query(IdempotencyKey)
            .filter(
                IdempotencyKey.idempotency_key == idempotency_key,
                IdempotencyKey.organizer_email == organizer_email,
            )
            .first()
        )
        if not existing:
            return None

        if existing.status == IdempotencyStatus.completed and existing.booking_id:
            return (
                self.db.query(Booking)
                .filter(Booking.id == existing.booking_id)
                .first()
            )

        if existing.status == IdempotencyStatus.in_progress:
            raise ConflictError(
                "A request with this Idempotency-Key is already in progress"
            )

        return None

    def _save_idempotency_key(
        self,
        idempotency_key: str,
        organizer_email: str,
        booking: Booking,
    ) -> None:
        record = IdempotencyKey(
            idempotency_key=idempotency_key,
            organizer_email=organizer_email,
            booking_id=booking.id,
            status=IdempotencyStatus.completed,
        )
        self.db.add(record)
        # No commit here — commit happens in create_booking
        # IntegrityError on unique constraint (key, organizer) fires at commit time