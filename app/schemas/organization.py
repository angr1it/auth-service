from typing import Optional

from pydantic import EmailStr

from fastapi_camelcase import CamelModel


class OrganizationCreateRequest(CamelModel):
    organization_name: str
    organization_slug: Optional[str] = None
    email: EmailStr
    login: str
    password: str

    operator_id: Optional[int] = None
