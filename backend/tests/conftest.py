
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.database import Base, get_db
from app.auth import get_current_user_id
from app.models.user import User
from app.models.document import Document
from app.models.chunk import DocumentChunk


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError(
        "TEST_DATABASE_URL is not set. "
        "Configure it before running tests."
    )

if "/securedocs_test" not in TEST_DATABASE_URL:
    raise RuntimeError(
        "Tests can only run against securedocs_test."
    )

test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_id] = lambda: 1

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def two_users_and_documents(db_session):
    alice = User(
        id=1,
        email="alice-test@example.com",
        password_hash="test-hash",
        role="user",
    )

    bob = User(
        id=2,
        email="bob-test@example.com",
        password_hash="test-hash",
        role="user",
    )

    db_session.add_all([alice, bob])
    db_session.flush()

    alice_doc = Document(
        user_id=alice.id,
        filename="alice.pdf",
        file_path="uploads/alice-test.pdf",
    )

    bob_doc = Document(
        user_id=bob.id,
        filename="bob.pdf",
        file_path="uploads/bob-test.pdf",
    )

    db_session.add_all([alice_doc, bob_doc])
    db_session.commit()

    db_session.refresh(alice_doc)
    db_session.refresh(bob_doc)

    return {
        "alice": alice_doc.id,
        "bob": bob_doc.id,
    }
