from typing import Optional

from pydantic import EmailStr, Field

from fastapi_camelcase import CamelModel


class OrganizationCreateRequest(CamelModel):
    organization_name: str = Field(..., example="Acme Corp")
    organization_slug: Optional[str] = Field(None, example="acme-corp")
    email: EmailStr = Field(..., example="owner@example.com")
    login: str = Field(..., example="owner")
    password: str = Field(..., example="secret")

    operator_id: Optional[int] = Field(None, example=42)

class OrganizationCreateResponse(CamelModel):
    organizationId: str = Field(..., example="acme-corp")