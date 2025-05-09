import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from api.login.auth import password as password_module
from api.login.auth import logout as logout_module
from api.login.auth import refresh as refresh_module
from api.login import user as user_module
from api.organization import create as create_module
from api.organization import invite as invite_module
from api.organization import register as register_module
from api.organization import user as org_user_module
from models.user import User


@pytest.fixture
def session_mock() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def app(session_mock: AsyncMock) -> FastAPI:
    app = FastAPI()
    app.include_router(password_module.router)
    app.include_router(logout_module.router)
    app.include_router(refresh_module.router)
    app.include_router(user_module.router)
    app.include_router(create_module.router)
    app.include_router(invite_module.router)
    app.include_router(register_module.router)
    app.include_router(org_user_module.router)

    async def _override_get_async_session():
        yield session_mock

    app.dependency_overrides[password_module.get_async_session] = (
        _override_get_async_session
    )
    app.dependency_overrides[logout_module.get_async_session] = (
        _override_get_async_session
    )
    app.dependency_overrides[refresh_module.get_async_session] = (
        _override_get_async_session
    )
    app.dependency_overrides[user_module.get_async_session] = (
        _override_get_async_session
    )
    app.dependency_overrides[create_module.get_async_session] = (
        _override_get_async_session
    )
    app.dependency_overrides[invite_module.get_async_session] = (
        _override_get_async_session
    )
    app.dependency_overrides[register_module.get_async_session] = (
        _override_get_async_session
    )
    app.dependency_overrides[org_user_module.get_async_session] = (
        _override_get_async_session
    )
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture
def user_stub() -> User:
    return User(
        id=1,
        organization_id="org123",
        email="test@example.com",
        login="tester",
        password_hash="$argon2id$v=19$m=102400,t=2,p=8$hash",
        perm_version=1,
    )
