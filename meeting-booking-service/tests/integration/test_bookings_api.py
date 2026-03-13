import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch


def create_room(client, name="Test Room", capacity=10):
    response = client.post("/rooms", json={
        "name": name,
        "capacity": capacity,
        "floor": 1,
        "amenities": []
    })
    return response.json()


def booking_payload(room_id, start_hour=9, end_hour=10):
    # Always next Monday
    now = datetime(2026, 3, 16, tzinfo=timezone.utc)
    start = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end = now.replace(hour=end_hour, minute=0, second=0, microsecond=0)
    return {
        "roomId": room_id,
        "title": "Team Sync",
        "organizerEmail": "user@example.com",
        "startTime": start.isoformat(),
        "endTime": end.isoformat(),
    }


# ── Happy path ───────────────────────────────────────────

def test_create_booking(client):
    room = create_room(client)
    response = client.post("/bookings", json=booking_payload(room["id"]))
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "confirmed"
    assert data["room_id"] == room["id"]


# ── Conflict ─────────────────────────────────────────────

def test_overlapping_booking_returns_409(client):
    room = create_room(client, name="Overlap Room")
    payload = booking_payload(room["id"], start_hour=9, end_hour=11)
    client.post("/bookings", json=payload)
    response = client.post("/bookings", json=payload)
    assert response.status_code == 409
    assert response.json()["error"] == "ConflictError"


def test_partial_overlap_returns_409(client):
    room = create_room(client, name="Partial Overlap Room")
    client.post("/bookings", json=booking_payload(room["id"], 9, 11))
    # Overlaps from 10–12
    response = client.post("/bookings", json=booking_payload(room["id"], 10, 12))
    assert response.status_code == 409


# ── Room not found ───────────────────────────────────────

def test_booking_unknown_room_returns_404(client):
    response = client.post("/bookings", json=booking_payload("nonexistent-room-id"))
    assert response.status_code == 404


# ── Idempotency ──────────────────────────────────────────

def test_idempotent_booking_same_key_returns_same_booking(client):
    room = create_room(client, name="Idempotent Room")
    payload = booking_payload(room["id"])
    headers = {"Idempotency-Key": "unique-key-001"}
    r1 = client.post("/bookings", json=payload, headers=headers)
    r2 = client.post("/bookings", json=payload, headers=headers)
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["id"] == r2.json()["id"]


# ── Cancellation ─────────────────────────────────────────

def test_cancel_booking(client):
    room = create_room(client, name="Cancel Room")
    # Book far in future so grace period passes
    now = datetime(2026, 6, 15, tzinfo=timezone.utc)  # future Monday
    payload = {
        "roomId": room["id"],
        "title": "Future Meeting",
        "organizerEmail": "user@example.com",
        "startTime": now.replace(hour=9).isoformat(),
        "endTime": now.replace(hour=10).isoformat(),
    }
    booking = client.post("/bookings", json=payload).json()
    response = client.post(f"/bookings/{booking['id']}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_cancel_already_cancelled_is_noop(client):
    room = create_room(client, name="Noop Room")
    now = datetime(2026, 6, 15, tzinfo=timezone.utc)
    payload = {
        "roomId": room["id"],
        "title": "Future Meeting",
        "organizerEmail": "user@example.com",
        "startTime": now.replace(hour=9).isoformat(),
        "endTime": now.replace(hour=10).isoformat(),
    }
    booking = client.post("/bookings", json=payload).json()
    client.post(f"/bookings/{booking['id']}/cancel")
    response = client.post(f"/bookings/{booking['id']}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

def test_cancel_within_1_hour_returns_400(client):
    room = create_room(client, name="Late Cancel Room")
    # Book on next Monday
    start = datetime(2026, 3, 16, 10, 0, tzinfo=timezone.utc)
    end = start + timedelta(hours=1)
    payload = {
        "roomId": room["id"],
        "title": "Imminent Meeting",
        "organizerEmail": "user@example.com",
        "startTime": start.isoformat(),
        "endTime": end.isoformat(),
    }
    booking = client.post("/bookings", json=payload).json()
    
    # Try cancelling 30 minutes before start
    cancel_time = start - timedelta(minutes=30)
    with patch("app.services.booking_service.datetime") as mock_dt:
        mock_dt.now.return_value = cancel_time
        mock_dt.timezone = timezone
        response = client.post(f"/bookings/{booking['id']}/cancel")
        
    assert response.status_code == 400
    assert "1 hour" in response.json()["message"]


# ── Cancelled booking doesn't block new booking ──────────

def test_cancelled_booking_does_not_block_new_booking(client):
    room = create_room(client, name="Unblock Room")
    now = datetime(2026, 6, 15, tzinfo=timezone.utc)
    payload = {
        "roomId": room["id"],
        "title": "Meeting",
        "organizerEmail": "user@example.com",
        "startTime": now.replace(hour=9).isoformat(),
        "endTime": now.replace(hour=10).isoformat(),
    }
    booking = client.post("/bookings", json=payload).json()
    client.post(f"/bookings/{booking['id']}/cancel")
    # Same slot should now be available
    response = client.post("/bookings", json=payload)
    assert response.status_code == 201