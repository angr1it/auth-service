from typing import Optional

from fastapi_camelcase import CamelModel
from pydantic import Field, AnyUrl

class InviteRequest(CamelModel):
    expires_in_hours: Optional[int] = Field(default=24, example=24)
    operator_id: Optional[int] = Field(None, example=100)

class InviteResponse(CamelModel):
    inviteToken: str = Field(..., example="<token>")
    url: AnyUrl = Field(..., example="https://.../<token>")