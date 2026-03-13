from pydantic import BaseModel, EmailStr, field_validator, model_validator
from datetime import datetime
from typing import List, Optional
from app.models.booking import BookingStatus


class BookingCreate(BaseModel):
    roomId: str
    title: str
    organizerEmail: EmailStr
    startTime: datetime
    endTime: datetime

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be empty")
        return v.strip()

    @model_validator(mode="after")
    def validate_time_range(self) -> "BookingCreate":
        if self.startTime >= self.endTime:
            raise ValueError("startTime must be before endTime")

        duration = (self.endTime - self.startTime).total_seconds() / 60
        if duration < 15:
            raise ValueError("booking duration must be at least 15 minutes")
        if duration > 240:
            raise ValueError("booking duration must not exceed 4 hours")

        return self


class BookingResponse(BaseModel):
    id: str
    room_id: str
    title: str
    organizer_email: str
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class BookingListResponse(BaseModel):
    items: List[BookingResponse]
    total: int
    limit: int
    offset: int