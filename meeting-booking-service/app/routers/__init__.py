from app.routers.rooms import router as rooms_router
from app.routers.bookings import router as bookings_router
from app.routers.reports import router as reports_router

__all__ = ["rooms_router", "bookings_router", "reports_router"]