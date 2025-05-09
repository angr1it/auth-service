from fastapi_camelcase import CamelModel


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
