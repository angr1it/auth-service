"""Tests for /login/user endpoint."""

from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from models.user import User
from models.organization import Organization
from schemas.token import JwtPayload
from tests.unit.api.mocks import session_mock, user_stub, client, app
from api.login import user as user_module


def test_current_user_success(client: TestClient, session_mock: AsyncMock, user_stub: User):
    """Return user info when token valid."""
    org = Organization(id=user_stub.organization_id, name="Org")
    execute_result = MagicMock()
    execute_result.first.return_value = (user_stub, org)
    session_mock.execute.return_value = execute_result

    with patch.object(user_module, "decode_access_token", return_value=JwtPayload(sub=user_stub.id, org=user_stub.organization_id, login=user_stub.login, pv=user_stub.perm_version, iat=0, exp=0, jti="x")), patch.object(user_module, "fetch_permissions", return_value={}):
        resp = client.get("/user", headers={"Authorization": "Bearer token"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == user_stub.id
    assert body["email"] == user_stub.email
    assert body["permissions"] == {}


def test_current_user_perm_changed(client: TestClient, session_mock: AsyncMock, user_stub: User):
    """Mismatch permission version returns 401."""
    org = Organization(id=user_stub.organization_id, name="Org")
    execute_result = MagicMock()
    execute_result.first.return_value = (user_stub, org)
    session_mock.execute.return_value = execute_result

    with patch.object(user_module, "decode_access_token", return_value=JwtPayload(sub=user_stub.id, org=user_stub.organization_id, login=user_stub.login, pv=user_stub.perm_version + 1, iat=0, exp=0, jti="x")):
        resp = client.get("/user", headers={"Authorization": "Bearer token"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Permissions changed; re\u2011authenticate"


def test_current_user_not_found(client: TestClient, session_mock: AsyncMock, user_stub: User):
    """Return 404 when user not present."""
    execute_result = MagicMock()
    execute_result.first.return_value = None
    session_mock.execute.return_value = execute_result

    with patch.object(user_module, "decode_access_token", return_value=JwtPayload(sub=1, org="org", login="l", pv=1, iat=0, exp=0, jti="x")):
        resp = client.get("/user", headers={"Authorization": "Bearer token"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "User not found"
