from pydantic import EmailStr, Field

from fastapi_camelcase import CamelModel


class LoginPasswordRequest(CamelModel):
    email: EmailStr = Field(..., example="test@test.com")
    password: str = Field(..., example="secret")
    organization_id: str = Field(..., example="org-slug")

class LoginPasswordResponse(CamelModel):
    accessToken: str = Field(..., example="<jwt>")
    refreshToken: str = Field(..., example="<jwt>")