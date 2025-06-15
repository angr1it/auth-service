"""Tests for /logout endpoint."""

from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from jose import JWTError

from tests.unit.api.mocks import session_mock, client, app
from api.login.auth import logout as logout_module


def test_logout_without_cookie(client: TestClient, session_mock: AsyncMock):
    """Always returns ok when no cookie provided."""
    resp = client.post("/logout")
    assert resp.status_code == 200
    assert resp.json()["detail"] == "ok"


def test_logout_invalid_token(client: TestClient, session_mock: AsyncMock):
    """Invalid refresh token is ignored."""
    with patch.object(logout_module.jwt, "decode", side_effect=JWTError("bad")):
        resp = client.post("/logout", cookies={"refreshToken": "bad"})
    assert resp.status_code == 200
    assert resp.json()["detail"] == "ok"
