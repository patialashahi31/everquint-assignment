from fastapi import FastAPI

from app.routers import rooms_router, bookings_router, reports_router
from app.exceptions import register_exception_handlers

app = FastAPI(
    title="Meeting Room Booking Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Exception handlers ───────────────────────────────────
register_exception_handlers(app)

# ── Routers ──────────────────────────────────────────────
app.include_router(rooms_router)
app.include_router(bookings_router)
app.include_router(reports_router)


# ── Health check ─────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
