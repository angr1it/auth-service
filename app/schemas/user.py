from typing import List, Optional

from pydantic import EmailStr, Field, AnyUrl
from fastapi_camelcase import CamelModel

from schemas import PaginationModel

class UserProfile(CamelModel):
    id: int = Field(..., example=1)
    email: EmailStr = Field(..., example="owner@example.com")
    login: str = Field(..., example="owner")
    avatar_url: AnyUrl | None = Field(default=None, description="URL аватара пользователя")
    permissions: dict[str, list[str]] | None = Field(default=None, example={"auth": ["OWNER"]})
    perm_version: int = Field(..., example=1)
    operator_id: Optional[int] = Field(default=None, example=42)


class UserOutput(UserProfile):
    pass


class PaginatedUsers(PaginationModel):
    items: List[UserOutput] = Field(...)
    total: int = Field(..., example=1)
    pages: int = Field(..., example=1)
