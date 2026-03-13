from pydantic import BaseModel, field_validator
from typing import List


class RoomCreate(BaseModel):
    name: str
    capacity: int
    floor: int
    amenities: List[str] = []

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()

    @field_validator("capacity")
    @classmethod
    def capacity_must_be_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("capacity must be at least 1")
        return v


class RoomResponse(BaseModel):
    id: str
    name: str
    capacity: int
    floor: int
    amenities: List[str]

    model_config = {"from_attributes": True}