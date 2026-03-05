import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test_rolefit.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    import os
    try:
        if os.path.exists("./test_rolefit.db"):
            os.remove("./test_rolefit.db")
    except PermissionError:
        pass


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
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


@pytest.fixture
def sample_user(client):
    """Register a test user and return auth headers + user data."""
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    reg = client.post("/api/auth/register", json=user_data)
    if reg.status_code == 400 and "already registered" in reg.text:
        login = client.post("/api/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        token = login.json()["access_token"]
    else:
        assert reg.status_code == 200, f"Registration failed: {reg.text}"
        token = reg.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    me = client.get("/api/auth/me", headers=headers)
    return {"headers": headers, "user": me.json(), "token": token}


@pytest.fixture
def auth_headers(sample_user):
    """Shortcut fixture for just the auth headers."""
    return sample_user["headers"]
