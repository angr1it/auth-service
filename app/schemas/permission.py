from fastapi_camelcase import CamelModel


class PermissionBase(CamelModel):
    permissions: dict[str, list[str]]


class PermissionEdit(PermissionBase):
    pass


class PermissionResponse(PermissionEdit):
    pass
