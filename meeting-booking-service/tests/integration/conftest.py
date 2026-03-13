import pytest
import subprocess
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db
from app.models.base import Base
import os

TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://meeting_room_service_user:meeting_room_service_pass@db:5432/meeting_room_service_test_db"
)


@pytest.fixture(scope="session", autouse=True)
def run_migrations():
    subprocess.run(["alembic", "upgrade", "head"], check=True)


@pytest.fixture(scope="session")
def db_engine(run_migrations):
    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def db_session_factory(db_engine):
    return sessionmaker(bind=db_engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def clean_tables(db_session_factory):
    yield
    db = db_session_factory()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
    finally:
        db.close()


@pytest.fixture
def db(db_session_factory):
    db = db_session_factory()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()