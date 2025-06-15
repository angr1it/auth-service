import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from tests.unit.helpers.mocks import _async_result_all
from core.permission.helpers import fetch_permissions
from models.permission import Permission
from models.resource import Resource


@pytest.mark.asyncio
async def test_fetch_permissions_valid(mocker):
    """Return permissions grouped by resource."""
    db = AsyncMock(spec=AsyncSession)

    resource = Resource(id=10, name="documents")
    permission = Permission(id=100, resource_id=10, code="read")

    db.execute.return_value = _async_result_all([(permission.code, resource.name)])

    permissions = await fetch_permissions(db=db, user_id=1)

    assert permissions == {"documents": ["read"]}
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_permissions_no_permissions(mocker):
    """Return empty dict when user has no permissions."""
    db = AsyncMock(spec=AsyncSession)

    db.execute.return_value = _async_result_all([])

    permissions = await fetch_permissions(db=db, user_id=1)

    assert permissions == {}
    db.execute.assert_awaited_once()
