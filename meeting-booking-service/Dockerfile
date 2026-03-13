# ── Stage 1: Builder ────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Runtime ────────────────────────────────────
FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /install/bin /usr/local/bin

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]