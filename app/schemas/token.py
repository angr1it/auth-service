from fastapi_camelcase import CamelModel
from pydantic import Field

class JwtPayload(CamelModel):
    sub: int
    org: str
    login: str
    iat: int
    exp: int
    jti: str
    pv: int


class JWKS(CamelModel):
    keys: list


class TokenMeta(CamelModel):
    sub: int
    org: str
    login: str
    pv: int
    exp: int

class JWKSResponse(CamelModel):
    keys: list[dict[str, list]] = Field(..., example=[{"kty": "RSA", "alg": "RS256", "use": "sig", "n": "...", "e": "AQAB", "kid": "0" }])