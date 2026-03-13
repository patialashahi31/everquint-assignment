import pytest


def test_create_room(client):
    response = client.post("/rooms", json={
        "name": "Conference Room A",
        "capacity": 10,
        "floor": 1,
        "amenities": ["projector", "whiteboard"]
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Conference Room A"
    assert data["capacity"] == 10
    assert "id" in data


def test_create_room_duplicate_name(client):
    client.post("/rooms", json={"name": "Room A", "capacity": 5, "floor": 1, "amenities": []})
    response = client.post("/rooms", json={"name": "room a", "capacity": 5, "floor": 1, "amenities": []})
    assert response.status_code == 409
    assert "already exists" in response.json()["message"]


def test_create_room_invalid_capacity(client):
    response = client.post("/rooms", json={"name": "Room B", "capacity": 0, "floor": 1, "amenities": []})
    assert response.status_code == 400


def test_list_rooms(client):
    client.post("/rooms", json={"name": "Room C", "capacity": 5, "floor": 1, "amenities": []})
    client.post("/rooms", json={"name": "Room D", "capacity": 10, "floor": 2, "amenities": ["projector"]})
    response = client.get("/rooms")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_rooms_filter_min_capacity(client):
    client.post("/rooms", json={"name": "Small Room", "capacity": 3, "floor": 1, "amenities": []})
    client.post("/rooms", json={"name": "Large Room", "capacity": 20, "floor": 2, "amenities": []})
    response = client.get("/rooms?minCapacity=10")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Large Room"


def test_list_rooms_filter_amenity(client):
    client.post("/rooms", json={"name": "Room E", "capacity": 5, "floor": 1, "amenities": ["projector"]})
    client.post("/rooms", json={"name": "Room F", "capacity": 5, "floor": 1, "amenities": ["whiteboard"]})
    response = client.get("/rooms?amenity=projector")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Room E"