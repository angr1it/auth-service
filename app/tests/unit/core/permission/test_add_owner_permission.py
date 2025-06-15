import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from tests.unit.helpers.mocks import _async_result_one_or_none
from core.permission.helpers import add_owner_permission_to_user
from models.permission import Permission
from models.resource import Resource
from models.user import User


@pytest.mark.asyncio
async def test_add_owner_permission_valid(mocker):
    """Add owner permission when resource exists."""
    db = AsyncMock(spec=AsyncSession)
    user = User(id=1)

    resource = Resource(id=10, name="organization")
    permission = Permission(id=100, resource_id=10, code="owner")

    db.execute.side_effect = [
        _async_result_one_or_none(resource),
        _async_result_one_or_none(permission),
        _async_result_one_or_none(None),
    ]

    await add_owner_permission_to_user(db=db, user_id=user.id, commit=True)

    db.add.assert_called_once()
    db.commit.assert_awaited_once()
    db.refresh.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_owner_permission_no_resource(mocker):
    """Raise error if required resource is missing."""
    db = AsyncMock(spec=AsyncSession)
    user = User(id=1)

    db.execute.side_effect = [
        _async_result_one_or_none(None),
    ]

    with pytest.raises(ValueError, match="Resource 'organization' not found"):
        await add_owner_permission_to_user(db=db, user_id=user.id, commit=False)

    db.add.assert_not_called()
    db.commit.assert_not_awaited()
    db.refresh.assert_not_awaited()
