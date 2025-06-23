from pydantic import Field, EmailStr

from fastapi_camelcase import CamelModel

class RegisterRequest(CamelModel):
    email: EmailStr = Field(..., example="new@example.com")
    login: str = Field(..., example="newuser")
    password: str = Field(..., example="secret", description="password hash")

class RegisterResponse(CamelModel):
    id: int = Field(..., example=5, description="id пользователя")