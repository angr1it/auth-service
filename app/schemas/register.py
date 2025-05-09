from pydantic import EmailStr

from fastapi_camelcase import CamelModel


class RegisterRequest(CamelModel):
    email: EmailStr
    login: str
    password: str
