from typing import List, Optional

from pydantic import EmailStr
from fastapi_camelcase import CamelModel

from schemas import PaginationModel


class UserProfile(CamelModel):
    id: int
    email: EmailStr
    login: str
    avatar_url: str | None = None
    permissions: dict[str, list[str]] | None = None
    perm_version: int
    operator_id: Optional[int] = None


class UserOutput(UserProfile):
    pass


class PaginatedUsers(PaginationModel):
    items: List[UserOutput]
    total: int
    pages: int
