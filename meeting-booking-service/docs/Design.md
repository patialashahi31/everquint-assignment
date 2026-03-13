# Design Document

## Data Model

### rooms
| Column | Type | Notes |
|--------|------|-------|
| id | UUID (String) | Primary key |
| name | String | Unique, case-insensitive via `lower(name)` index |
| capacity | Integer | >= 1 |
| floor | Integer | |
| amenities | String[] | Postgres ARRAY |

### bookings
| Column | Type | Notes |
|--------|------|-------|
| id | UUID (String) | Primary key |
| room_id | String | FK → rooms |
| title | String | |
| organizer_email | String | |
| start_time | DateTime (TZ) | |
| end_time | DateTime (TZ) | |
| status | Enum | `confirmed` / `cancelled` |
| created_at | DateTime (TZ) | |

### idempotency_keys
| Column | Type | Notes |
|--------|------|-------|
| id | UUID (String) | Primary key |
| idempotency_key | String | Unique per organizer |
| organizer_email | String | |
| booking_id | String | FK → bookings (nullable) |
| status | Enum | `in_progress` / `completed` / `failed` |
| response_body | JSON | Cached response |
| created_at | DateTime (TZ) | |

Unique constraint: `(idempotency_key, organizer_email)`

---

## How Overlaps Are Enforced

Two layers of protection:

**1. Application layer** — before inserting a booking, we query for any confirmed booking where:
```
existing.start_time < new.end_time AND existing.end_time > new.start_time
```
This catches all overlap cases: full overlap, partial overlap, and containment.

**2. Concurrency layer** — we use `SELECT FOR UPDATE` on the room's bookings before the overlap check. This acquires a row-level lock so concurrent requests are serialized — only one can proceed at a time per room.

Cancelled bookings are excluded from overlap checks via `status = confirmed` filter.

---

## Error Handling Strategy

All errors follow a consistent JSON format:
```json
{
  "error": "ErrorType",
  "message": "Human readable message"
}
```

Three custom exception classes:
- `NotFoundError` → 404
- `ConflictError` → 409
- `ValidationError` → 400

Pydantic validation errors (wrong types, missing fields) are caught by a global `RequestValidationError` handler and formatted the same way.

A catch-all `Exception` handler returns 500 so no raw stacktraces ever leak to clients.

---

## How Idempotency Is Implemented

**Design choice:** Keys are unique per `(idempotency_key, organizer_email)`. This means the same key used by different organizers is treated as distinct — simplest model that prevents accidental cross-user conflicts.

**Flow:**
1. On `POST /bookings` with `Idempotency-Key` header, check `idempotency_keys` table for existing record
2. If found with `status = completed` → return cached booking immediately, no DB writes
3. If found with `status = in_progress` → return 409 (concurrent request in flight)
4. If not found → proceed with booking creation

---

## How Concurrency Is Handled

Two mechanisms work together:

**1. SELECT FOR UPDATE** — when checking for overlaps, we first lock the room's booking rows:
```python
self.db.query(Booking).filter(
    Booking.room_id == room_id
).with_for_update().first()
```
This prevents two concurrent requests from both passing the overlap check simultaneously.

**2. Unique constraint on idempotency_keys** — `(idempotency_key, organizer_email)` is enforced at the DB level. Even if two concurrent requests slip through the application-level check, only one INSERT can succeed. The second hits an `IntegrityError` which we catch and return as a 409.

**Limitation:** `SELECT FOR UPDATE` is an in-process DB lock. It works correctly for this assignment but in a multi-instance deployment you would want advisory locks or a distributed lock (e.g. Redis SETNX) for stronger guarantees.

---

## How Utilization Is Calculated

**Formula:**
```
utilizationPercent = total_booked_hours / total_business_hours
```

**Total business hours** = sum of available business time in `[from, to]` range, counting only Mon–Fri, 08:00–20:00, clamped to the report boundaries.

**Total booked hours** = sum of confirmed booking durations, clamped to the report range:
```python
effective_start = max(booking.start_time, from_time)
effective_end = min(booking.end_time, to_time)
hours = (effective_end - effective_start).total_seconds() / 3600
```

**Assumptions:**
- All times are treated as UTC
- Cancelled bookings are excluded
- Partial overlaps with the report range are clamped, not excluded
- If no business hours exist in range (e.g. weekend-only range), utilization = 0.0