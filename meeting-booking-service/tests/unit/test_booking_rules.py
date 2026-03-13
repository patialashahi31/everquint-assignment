import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

from app.services.booking_service import BookingService
from app.exceptions import ValidationError, ConflictError


def make_service():
    return BookingService(db=MagicMock())


# ── Working hours ────────────────────────────────────────

def test_rejects_weekend():
    service = make_service()
    start = datetime(2026, 3, 14, 9, 0, tzinfo=timezone.utc)  # Saturday
    end = datetime(2026, 3, 14, 10, 0, tzinfo=timezone.utc)
    with pytest.raises(ValidationError, match="Monday to Friday"):
        service._validate_working_hours(start, end)


def test_rejects_before_business_hours():
    service = make_service()
    start = datetime(2026, 3, 16, 7, 0, tzinfo=timezone.utc)  # Monday 7am
    end = datetime(2026, 3, 16, 8, 0, tzinfo=timezone.utc)
    with pytest.raises(ValidationError, match="must start between"):
        service._validate_working_hours(start, end)


def test_rejects_after_business_hours():
    service = make_service()
    start = datetime(2026, 3, 16, 19, 0, tzinfo=timezone.utc)
    end = datetime(2026, 3, 16, 20, 30, tzinfo=timezone.utc)
    with pytest.raises(ValidationError, match="must end by"):
        service._validate_working_hours(start, end)


def test_rejects_end_exactly_past_20():
    service = make_service()
    start = datetime(2026, 3, 16, 19, 0, tzinfo=timezone.utc)
    end = datetime(2026, 3, 16, 20, 1, tzinfo=timezone.utc)
    with pytest.raises(ValidationError, match="must end by"):
        service._validate_working_hours(start, end)


def test_accepts_valid_business_hours():
    service = make_service()
    start = datetime(2026, 3, 16, 9, 0, tzinfo=timezone.utc)
    end = datetime(2026, 3, 16, 10, 0, tzinfo=timezone.utc)
    service._validate_working_hours(start, end)  # should not raise


# ── Duration ─────────────────────────────────────────────

def test_rejects_duration_less_than_15_minutes():
    from app.schemas.booking import BookingCreate
    with pytest.raises(Exception, match="at least 15 minutes"):
        BookingCreate(
            roomId="room-1",
            title="Test",
            organizerEmail="test@test.com",
            startTime=datetime(2026, 3, 16, 9, 0, tzinfo=timezone.utc),
            endTime=datetime(2026, 3, 16, 9, 10, tzinfo=timezone.utc),
        )


def test_rejects_duration_more_than_4_hours():
    from app.schemas.booking import BookingCreate
    with pytest.raises(Exception, match="exceed 4 hours"):
        BookingCreate(
            roomId="room-1",
            title="Test",
            organizerEmail="test@test.com",
            startTime=datetime(2026, 3, 16, 9, 0, tzinfo=timezone.utc),
            endTime=datetime(2026, 3, 16, 13, 30, tzinfo=timezone.utc),
        )


def test_rejects_start_after_end():
    from app.schemas.booking import BookingCreate
    with pytest.raises(Exception, match="before endTime"):
        BookingCreate(
            roomId="room-1",
            title="Test",
            organizerEmail="test@test.com",
            startTime=datetime(2026, 3, 16, 10, 0, tzinfo=timezone.utc),
            endTime=datetime(2026, 3, 16, 9, 0, tzinfo=timezone.utc),
        )