from pydantic import BaseModel


class RoomUtilizationReport(BaseModel):
    roomId: str
    roomName: str
    totalBookingHours: float
    utilizationPercent: float