from fastapi_camelcase import CamelModel
from pydantic import Field

class PermissionBase(CamelModel):
    permissions: dict[str, list[str]] = Field(..., example={ "calls": ["READ", "WRITE"] })


class PermissionEdit(PermissionBase):
    pass


class PermissionResponse(PermissionEdit):
    pass
