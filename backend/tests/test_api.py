"""Integration tests for API endpoints."""
import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def _unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def _register_and_get_headers(c=None):
    c = c or client
    email = _unique_email()
    reg = c.post("/api/auth/register", json={
        "name": "Test User",
        "email": email,
        "password": "TestPass123!"
    })
    assert reg.status_code == 200
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, email


class TestHealthAndRoot:
    def test_health(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "healthy"}

    def test_root(self):
        r = client.get("/")
        assert r.status_code == 200
        assert "RoleFit" in r.json()["message"]

    def test_404_handler(self):
        r = client.get("/api/nonexistent-route")
        assert r.status_code == 404
        data = r.json()
        assert data["error"] is True


class TestSecurityHeaders:
    def test_x_content_type_options(self):
        r = client.get("/health")
        assert r.headers.get("X-Content-Type-Options") == "nosniff"

    def test_x_frame_options(self):
        r = client.get("/health")
        assert r.headers.get("X-Frame-Options") == "DENY"

    def test_x_xss_protection(self):
        r = client.get("/health")
        assert r.headers.get("X-XSS-Protection") == "1; mode=block"

    def test_referrer_policy(self):
        r = client.get("/health")
        assert r.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


class TestAuth:
    def test_register_success(self):
        email = _unique_email()
        r = client.post("/api/auth/register", json={
            "name": "New User",
            "email": email,
            "password": "StrongPass123!"
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_email(self):
        email = _unique_email()
        client.post("/api/auth/register", json={
            "name": "First",
            "email": email,
            "password": "StrongPass123!"
        })
        r = client.post("/api/auth/register", json={
            "name": "Second",
            "email": email,
            "password": "AnotherPass123!"
        })
        assert r.status_code == 400

    def test_login_success(self):
        email = _unique_email()
        client.post("/api/auth/register", json={
            "name": "Login User",
            "email": email,
            "password": "LoginPass123!"
        })
        r = client.post("/api/auth/login", json={
            "email": email,
            "password": "LoginPass123!"
        })
        assert r.status_code == 200
        assert "access_token" in r.json()

    def test_login_wrong_password(self):
        email = _unique_email()
        client.post("/api/auth/register", json={
            "name": "Wrong PW",
            "email": email,
            "password": "CorrectPass123!"
        })
        r = client.post("/api/auth/login", json={
            "email": email,
            "password": "WrongPassword"
        })
        assert r.status_code == 401

    def test_me_unauthorized(self):
        r = client.get("/api/auth/me")
        assert r.status_code in (401, 403)

    def test_me_with_token(self):
        headers, email = _register_and_get_headers()
        r = client.get("/api/auth/me", headers=headers)
        assert r.status_code == 200
        assert r.json()["email"] == email

    def test_update_prefer_local_model(self):
        headers, _ = _register_and_get_headers()
        r = client.put("/api/auth/me", headers=headers, json={"prefer_local_model": True})
        assert r.status_code == 200
        me = client.get("/api/auth/me", headers=headers)
        assert me.json()["prefer_local_model"] is True


class TestFileUploadValidation:
    def test_reject_unsupported_file_type(self):
        headers, _ = _register_and_get_headers()
        r = client.post(
            "/api/resume/upload",
            headers=headers,
            files={"file": ("test.exe", b"malicious content", "application/octet-stream")}
        )
        assert r.status_code == 400
        assert "Unsupported file type" in r.json()["detail"]

    def test_reject_empty_file(self):
        headers, _ = _register_and_get_headers()
        r = client.post(
            "/api/resume/upload",
            headers=headers,
            files={"file": ("test.txt", b"", "text/plain")}
        )
        assert r.status_code == 400
        assert "empty" in r.json()["detail"].lower() or "extract" in r.json()["detail"].lower()

    def test_resume_upload_no_auth(self):
        r = client.post(
            "/api/resume/upload",
            files={"file": ("test.txt", b"Some resume content", "text/plain")}
        )
        assert r.status_code in (401, 403)


class TestJobInputValidation:
    def test_reject_too_long_text(self):
        headers, _ = _register_and_get_headers()
        r = client.post(
            "/api/jobs/parse",
            headers=headers,
            json={"raw_text": "x" * 25_000}
        )
        assert r.status_code == 400
        assert "too long" in r.json()["detail"]

    def test_reject_invalid_url_scheme(self):
        headers, _ = _register_and_get_headers()
        r = client.post(
            "/api/jobs/parse",
            headers=headers,
            json={"source_url": "ftp://evil.com/job"}
        )
        assert r.status_code == 400
        assert "http" in r.json()["detail"].lower()

    def test_reject_empty_text(self):
        headers, _ = _register_and_get_headers()
        r = client.post(
            "/api/jobs/parse",
            headers=headers,
            json={"raw_text": "   "}
        )
        assert r.status_code == 400


class TestOllamaStatus:
    def test_ollama_status_endpoint(self):
        r = client.get("/api/advanced/ollama-status")
        assert r.status_code == 200
        data = r.json()
        assert "available" in data
        assert "model" in data
