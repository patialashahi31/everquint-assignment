# Meeting Room Booking Service

A production-grade REST API for booking meeting rooms, built with FastAPI, PostgreSQL, and Docker.

## Tech Stack

- **Python 3.13** + **FastAPI**
- **PostgreSQL 16**
- **SQLAlchemy 2.0** (ORM)
- **Alembic** (migrations)
- **Pytest** (unit + integration tests)
- **Docker** + **Docker Compose**

## Project Structure

```
meeting-room-service/
├── docs/                    # System design & architecture docs
├── app/
│   ├── main.py              # FastAPI app init
│   ├── database.py          # DB engine + session
│   ├── exceptions.py        # Custom exceptions + global handlers
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── routers/             # Route handlers (no business logic)
│   └── services/            # All business logic
├── tests/
│   ├── unit/                # Pure logic tests, no DB
│   └── integration/         # API tests against real DB
├── alembic/                 # DB migrations
├── scripts/
│   └── init_db.sql          # Creates test DB on first run
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── requirements.txt
```

## Documentation

Detailed API flows, database models, and system architecture mapping can be found in the `docs/` directory:

- [System Design Document](docs/Design.md)
- [API Documentation](docs/docs.png)

## Prerequisites

- Docker (Make sure Docker is running)
- Docker Compose
- Make

## Quick Start

```bash
# 1. Clone the repo
git clone <repo-url>
cd meeting-room-service

# 2. Build images
make build

# 3. Start DB + app
make up

# 4. Run migrations
make migrate

# 5. Visit API docs
open http://localhost:8000/docs
```

## API Endpoints

| Method | Path                        | Description                              |
| ------ | --------------------------- | ---------------------------------------- |
| POST   | `/rooms`                    | Create a room                            |
| GET    | `/rooms`                    | List rooms (filter by capacity, amenity) |
| POST   | `/bookings`                 | Create a booking (idempotent)            |
| GET    | `/bookings`                 | List bookings (paginated)                |
| POST   | `/bookings/{id}/cancel`     | Cancel a booking                         |
| GET    | `/reports/room-utilization` | Room utilization report                  |
| GET    | `/health`                   | Health check                             |

## Running Tests

```bash
# All tests
make test

# Unit tests only
make test-unit

# Integration tests only
make test-integration

# Reset test container + image
make test-reset
```

## Database Commands

```bash
# Apply migrations
make migrate

# Roll back one migration
make migrate-down

# View migration history
make migrate-history

# Open DB shell
make db-shell
```

## Makefile Commands

| Command        | Description                    |
| -------------- | ------------------------------ |
| `make build`   | Build Docker images            |
| `make up`      | Start app + DB                 |
| `make down`    | Stop containers                |
| `make reset`   | Stop containers + wipe volumes |
| `make logs`    | Tail app logs                  |
| `make migrate` | Apply all migrations           |
| `make test`    | Run full test suite            |
| `make shell`   | Bash into app container        |
| `make lint`    | Run ruff linter                |
| `make format`  | Run ruff formatter             |

## Business Rules

- Bookings only allowed **Mon–Fri, 08:00–20:00**
- Duration between **15 minutes and 4 hours**
- No overlapping confirmed bookings for the same room
- Cancellation allowed up to **1 hour before** start time
- Cancelled bookings do **not** block new bookings
- Idempotent booking creation via `Idempotency-Key` header

## Error Format

All errors return consistent JSON:

```json
{
  "error": "ValidationError",
  "message": "startTime must be before endTime"
}
```
