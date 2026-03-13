#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
    CREATE DATABASE meeting_room_service_test_db;
    GRANT ALL PRIVILEGES ON DATABASE meeting_room_service_test_db TO $POSTGRES_USER;
EOSQL