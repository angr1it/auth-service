from pydantic import EmailStr

from fastapi_camelcase import CamelModel


class LoginPasswordRequest(CamelModel):
    email: EmailStr
    password: str
    organization_id: str
