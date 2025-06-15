"""Tests for /login/refresh endpoint."""

from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from jose import JWTError

from tests.unit.api.mocks import session_mock, client, app
from api.login.auth import refresh as refresh_module


def test_login_refresh_missing_cookie(client: TestClient):
    """401 when cookie absent."""
    resp = client.get("/refresh")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Missing refresh token"


def test_login_refresh_invalid_token(client: TestClient, session_mock: AsyncMock):
    """401 when token decode fails."""
    with patch.object(refresh_module.jwt, "decode", side_effect=JWTError("bad")):
        resp = client.get("/refresh", cookies={"refreshToken": "bad"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid refresh token"
