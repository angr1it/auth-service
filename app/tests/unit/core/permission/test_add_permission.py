import pytest

from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from tests.unit.helpers.mocks import _async_result_one_or_none
from core.permission.helpers import add_permissions_to_user
from models.permission import Permission
from models.resource import Resource
from models.user import User


@pytest.mark.asyncio
async def test_add_permissions_valid(mocker):
    """Valid permissions are added and committed."""
    db = AsyncMock(spec=AsyncSession)
    user = User(id=1)

    resource = Resource(id=10, name="documents")
    permission = Permission(id=100, resource_id=10, code="read")

    db.execute.side_effect = [
        _async_result_one_or_none(resource),
        _async_result_one_or_none(permission),
        _async_result_one_or_none(None),
    ]

    permissions_dict = {"documents": ["read"]}

    await add_permissions_to_user(
        db=db,
        user_id=user.id,  # Fixed argument
        permissions_dict=permissions_dict,
        ignore_invalid=False,
        commit=True,
    )

    db.add.assert_called_once()
    db.commit.assert_awaited_once()
    db.refresh.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_permissions_ignore_invalid_resource(mocker):
    """Ignore invalid resource when flag set."""
    db = AsyncMock(spec=AsyncSession)
    user = User(id=1)

    db.execute.return_value.scalar_one_or_none = lambda: None

    permissions_dict = {"nonexistent": ["read"]}

    await add_permissions_to_user(
        db=db,
        user_id=user.id,
        permissions_dict=permissions_dict,
        ignore_invalid=True,
        commit=False,
    )

    db.add.assert_not_called()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_permissions_invalid_permission_raises():
    """Raise error when permission not found."""
    db = AsyncMock(spec=AsyncSession)
    user = User(id=1)
    resource = Resource(id=1, name="docs")

    db.execute.side_effect = [
        _async_result_one_or_none(resource),
        _async_result_one_or_none(None),
    ]

    permissions_dict = {"docs": ["write"]}

    with pytest.raises(ValueError, match="Permission 'write' not found"):
        await add_permissions_to_user(
            db=db,
            user_id=user.id,
            permissions_dict=permissions_dict,
            ignore_invalid=False,
            commit=False,
        )
