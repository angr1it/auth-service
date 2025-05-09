from datetime import datetime as dt
from datetime import timezone, timedelta
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import ensure_owner
from models.registration_token import RegistrationToken
from schemas.invite import InviteRequest
from schemas.token import TokenMeta
from config.db import get_async_session
from utils.helpers.jwt import sign_jwt
from config import app_settings

router = APIRouter()


@router.post("/invite")
async def invite_user(
    body: InviteRequest,
    payload: Annotated[TokenMeta, Depends(ensure_owner)],
    sess: AsyncSession = Depends(get_async_session),
):
    now = dt.now(timezone.utc)
    jti = uuid4().hex
    exp = now + timedelta(hours=body.expires_in_hours)
    token = sign_jwt(
        {
            "jti": jti,
            "org": payload.org,
            "typ": "invite",
            "op": body.operator_id,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
        }
    )
    sess.add(
        RegistrationToken(
            jti=jti,
            organization_id=payload.org,
            created_by=payload.sub,
            expires_at=exp,
            operator_id=body.operator_id,
        )
    )

    await sess.commit()
    return {
        "inviteToken": token,
        "url": f"{app_settings.registration_token_url_prefix}/{token}",
    }
