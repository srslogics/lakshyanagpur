import os
os.environ["DATABASE_URL"] = "sqlite:///./test_lakshya.db"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["SEED_DEMO_DATA"] = "false"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models import User
from app.security import create_token, hash_password

engine = create_engine("sqlite:///./test_lakshya.db", connect_args={"check_same_thread": False})
TestingSession = sessionmaker(bind=engine, expire_on_commit=False)

@pytest.fixture(autouse=True)
def database():
    Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
    db = TestingSession()
    owner = User(email="owner@example.com", full_name="Owner", role="owner", password_hash=hash_password("Password123!"))
    parent = User(email="parent@example.com", full_name="Parent", role="parent_student", password_hash=hash_password("Password123!"))
    db.add_all([owner, parent]); db.commit()
    yield db
    db.close(); Base.metadata.drop_all(engine)

@pytest.fixture
def client(database):
    def override_db():
        yield database
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client: yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def owner_headers(database):
    user = database.query(User).filter_by(role="owner").one()
    return {"Authorization": f"Bearer {create_token(user)}"}

@pytest.fixture
def parent_headers(database):
    user = database.query(User).filter_by(role="parent_student").one()
    return {"Authorization": f"Bearer {create_token(user)}"}
