.PHONY: build up down logs restart migrate migrate-create migrate-down migrate-history test test-unit test-integration shell lint format db-init reset db-shell

# ── Docker ───────────────────────────────────────────────
setup:
	chmod +x scripts/init-db.sh

build: setup
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f app

restart:
	docker compose restart app

reset:
	docker compose down -v

# ── Database ─────────────────────────────────────────────
db-init:
	alembic init alembic

# Runs locally — generates migration file locally
migrate-create:
	alembic revision --autogenerate -m "$(msg)"

migrate:
	docker compose exec app alembic upgrade head

migrate-down:
	docker compose exec app alembic downgrade -1

migrate-history:
	docker compose exec app alembic history --verbose

db-shell:
	docker compose exec db psql -U meeting_room_service_user -d meeting_room_service_db

# ── Tests ────────────────────────────────────────────────
test:
	docker compose --profile test run --rm test

test-unit:
	docker compose --profile test run --rm test pytest tests/unit/ -v

test-integration:
	docker compose --profile test run --rm test pytest tests/integration/ -v

test-reset:
	docker compose --profile test rm -f -s -v test
	docker rmi -f $$(docker images -q meeting-booking-service_test 2>/dev/null) 2>/dev/null || true

# ── Dev ──────────────────────────────────────────────────
shell:
	docker compose exec app bash

lint:
	ruff check app/ tests/

format:
	ruff format app/ tests/