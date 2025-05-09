import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from models.user import User
from tests.api.mocks import session_mock, user_stub, client, app
from api.login.auth import password as password_module


def test_login_password_success(
    client: TestClient, session_mock: AsyncMock, user_stub: User
):
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = user_stub
    session_mock.execute.return_value = execute_result

    with patch.object(
        password_module.argon2, "verify", return_value=True
    ), patch.object(
        password_module, "issue_access_token", return_value="access"
    ), patch.object(
        password_module, "issue_refresh_token", return_value="refresh"
    ):

        resp = client.post(
            "/password",
            json={
                "email": "test@example.com",
                "password": "secret",
                "organization_id": "org123",
            },
        )

    assert resp.status_code == 200
    assert resp.json() == {"accessToken": "access", "refreshToken": "refresh"}
    session_mock.commit.assert_awaited_once()

    set_cookie = resp.headers.get("set-cookie")
    assert set_cookie is not None, "Ожидался заголовок Set-Cookie"

    assert "accessToken=access" in set_cookie, f"Не нашли accessToken в {set_cookie!r}"
    assert (
        "refreshToken=refresh" in set_cookie
    ), f"Не нашли refreshToken в {set_cookie!r}"


def test_login_password_invalid_credentials(
    client: TestClient, session_mock: AsyncMock
):
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None
    session_mock.execute.return_value = execute_result

    with patch.object(password_module.argon2, "verify", return_value=False):
        resp = client.post(
            "/password",
            json={
                "email": "bad@example.com",
                "password": "wrong",
                "organization_id": "org123",
            },
        )

    assert resp.status_code == 400
    assert resp.json() == {"detail": "Bad credentials"}
