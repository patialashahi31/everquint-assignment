from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from app.models.room import Room
from app.models.booking import Booking, BookingStatus
from app.schemas.report import RoomUtilizationReport


BUSINESS_START_HOUR = 8
BUSINESS_END_HOUR = 20


class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def room_utilization(
        self, from_time: datetime, to_time: datetime
    ) -> list[RoomUtilizationReport]:
        rooms = self.db.query(Room).all()
        total_business_hours = self._calculate_total_business_hours(from_time, to_time)

        results = []
        for room in rooms:
            bookings = (
                self.db.query(Booking)
                .filter(
                    Booking.room_id == room.id,
                    Booking.status == BookingStatus.confirmed,
                    Booking.start_time < to_time,
                    Booking.end_time > from_time,
                )
                .all()
            )

            booked_hours = sum(
                self._clamp_duration(b.start_time, b.end_time, from_time, to_time)
                for b in bookings
            )

            utilization = (
                round(booked_hours / total_business_hours, 4)
                if total_business_hours > 0
                else 0.0
            )

            results.append(
                RoomUtilizationReport(
                    roomId=room.id,
                    roomName=room.name,
                    totalBookingHours=round(booked_hours, 2),
                    utilizationPercent=utilization,
                )
            )

        return results

    # ── Private helpers ──────────────────────────────────

    def _clamp_duration(
        self,
        start: datetime,
        end: datetime,
        from_time: datetime,
        to_time: datetime,
    ) -> float:
        # Clamp booking to the report range
        effective_start = max(start, from_time)
        effective_end = min(end, to_time)
        duration = (effective_end - effective_start).total_seconds() / 3600
        return max(duration, 0.0)

    def _calculate_total_business_hours(
        self, from_time: datetime, to_time: datetime
    ) -> float:
        total_hours = 0.0
        current = from_time.replace(hour=0, minute=0, second=0, microsecond=0)

        while current < to_time:
            if current.weekday() < 5:  # Mon–Fri
                # Business window for this day
                day_start = current.replace(hour=BUSINESS_START_HOUR)
                day_end = current.replace(hour=BUSINESS_END_HOUR)

                # Clamp to the report range
                effective_start = max(day_start, from_time)
                effective_end = min(day_end, to_time)

                if effective_end > effective_start:
                    total_hours += (
                        effective_end - effective_start
                    ).total_seconds() / 3600

            current += timedelta(days=1)

        return total_hours