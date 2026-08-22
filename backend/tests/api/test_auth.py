"""Tests for POST /auth/sso."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
import pytest
from fastapi.testclient import TestClient

import utils.auth as auth_module
from main import app
from utils.auth import (
    SESSION_TOKEN_AUDIENCE,
    SESSION_TOKEN_ISSUER,
    SITE_TOKEN_AUDIENCE,
    SITE_TOKEN_ISSUER,
    verify_session_token,
)
from utils.config import Settings

SSO_SECRET = "test-sso-shared-secret-at-least-32b"
SESSION_SECRET = "test-frontline-session-secret-32b"
COMPANY_ID = UUID("11111111-1111-1111-1111-111111111111")


@pytest.fixture
def client(monkeypatch):
    settings = Settings(
        _env_file=None,
        SSO_SHARED_SECRET=SSO_SECRET,
        FRONTLINE_SESSION_SECRET=SESSION_SECRET,
        DEV_COMPANY_ID=str(COMPANY_ID),
    )
    monkeypatch.setattr(auth_module, "get_settings", lambda: settings)
    return TestClient(app)


def _site_token(
    *,
    secret: str = SSO_SECRET,
    exp_delta: timedelta = timedelta(seconds=60),
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(COMPANY_ID),
        "company_name": "Acme Srl",
        "iss": SITE_TOKEN_ISSUER,
        "aud": SITE_TOKEN_AUDIENCE,
        "iat": now,
        "exp": now + exp_delta,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def test_sso_exchange_returns_session_token(client):
    response = client.post("/auth/sso", json={"sso_token": _site_token()})

    assert response.status_code == 200
    session_token = response.json()["session_token"]
    assert verify_session_token(session_token) == COMPANY_ID

    decoded = jwt.decode(
        session_token,
        SESSION_SECRET,
        algorithms=["HS256"],
        audience=SESSION_TOKEN_AUDIENCE,
        issuer=SESSION_TOKEN_ISSUER,
    )
    assert decoded["sub"] == str(COMPANY_ID)


def test_sso_exchange_rejects_expired_token(client):
    response = client.post(
        "/auth/sso",
        json={"sso_token": _site_token(exp_delta=timedelta(seconds=-120))},
    )
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()


def test_sso_exchange_rejects_wrong_signature(client):
    response = client.post(
        "/auth/sso",
        json={"sso_token": _site_token(secret="wrong-secret-that-is-long-enough-32")},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid SSO token"


def test_sso_exchange_rejects_empty_body(client):
    response = client.post("/auth/sso", json={"sso_token": ""})
    assert response.status_code == 422
