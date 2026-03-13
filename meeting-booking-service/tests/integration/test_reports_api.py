from datetime import datetime, timezone


def create_room(client, name="Report Room"):
    return client.post("/rooms", json={
        "name": name, "capacity": 10, "floor": 1, "amenities": []
    }).json()


def test_utilization_no_bookings(client):
    create_room(client, "Empty Room")
    response = client.get("/reports/room-utilization?from=2026-03-16T08:00:00Z&to=2026-03-20T20:00:00Z")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["totalBookingHours"] == 0.0
    assert data[0]["utilizationPercent"] == 0.0


def test_utilization_with_bookings(client):
    room = create_room(client, "Busy Room")
    # Book 2 hours on Monday
    client.post("/bookings", json={
        "roomId": room["id"],
        "title": "Meeting",
        "organizerEmail": "user@example.com",
        "startTime": "2026-03-16T09:00:00Z",
        "endTime": "2026-03-16T11:00:00Z",
    })
    response = client.get("/reports/room-utilization?from=2026-03-16T08:00:00Z&to=2026-03-20T20:00:00Z")
    assert response.status_code == 200
    data = [r for r in response.json() if r["roomId"] == room["id"]][0]
    assert data["totalBookingHours"] == 2.0
    # 5 days x 12 hours = 60 total business hours
    assert data["utilizationPercent"] == round(2.0 / 60, 4)


def test_utilization_partial_overlap(client):
    room = create_room(client, "Overlap Report Room")
    # Booking starts before 'from' range
    client.post("/bookings", json={
        "roomId": room["id"],
        "title": "Early Meeting",
        "organizerEmail": "user@example.com",
        "startTime": "2026-03-16T08:00:00Z",
        "endTime": "2026-03-16T10:00:00Z",
    })
    # Report from 09:00 — only 1 hour should count
    response = client.get("/reports/room-utilization?from=2026-03-16T09:00:00Z&to=2026-03-20T20:00:00Z")
    data = [r for r in response.json() if r["roomId"] == room["id"]][0]
    assert data["totalBookingHours"] == 1.0