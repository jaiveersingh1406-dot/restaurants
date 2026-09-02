import mysql.connector 
from fastapi import HTTPException
from app.router.auth import login
from app.schema.schema import login as LoginSchema
from app.service.service import get_signup


def test_get_signup_raises_http_exception_when_db_fails(monkeypatch):
    def fake_get_connection():
        raise mysql.connector.DatabaseError("Can't connect to MySQL server on 'localhost:3306' (1)")

    monkeypatch.setattr("app.service.service.get_connection", fake_get_connection)

    try:
        get_signup("testuser", "test@example.com", "secret123")
        assert False, "HTTPException was not raised"
    except HTTPException as exc:
        assert exc.status_code == 500
        assert "Database error while signing up" in exc.detail


def test_login_uses_admin_service_when_role_is_admin(monkeypatch):
    def fake_get_admin_login(email, password):
        return {"email": email, "password": password, "role": "admin"}

    def fake_get_login(email, password):
        return {"email": email, "password": password, "role": "user"}

    monkeypatch.setattr("app.router.auth.get_admin_login", fake_get_admin_login)
    monkeypatch.setattr("app.router.auth.get_login", fake_get_login)

    result = login(LoginSchema(email="admin@example.com", password="secret1234", role="admin"))

    assert result["message"] == "Admin login successful"
    assert result["user"]["role"] == "admin"
