from typing import Optional

from fastapi_camelcase import CamelModel


class InviteRequest(CamelModel):
    expires_in_hours: Optional[int] = 24
    operator_id: Optional[int] = None
