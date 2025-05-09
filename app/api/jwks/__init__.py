import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from fastapi import APIRouter

from config import app_settings


router = APIRouter()


def _rsa_public_numbers_from_pem(pem: str):
    key = serialization.load_pem_public_key(pem.encode(), backend=default_backend())
    if not isinstance(key, rsa.RSAPublicKey):
        raise ValueError("Public key is not RSA")
    numbers = key.public_numbers()
    return numbers.n, numbers.e


n_int, e_int = _rsa_public_numbers_from_pem(app_settings.jwt_public_key)

n = (
    base64.urlsafe_b64encode(n_int.to_bytes((n_int.bit_length() + 7) // 8, "big"))
    .rstrip(b"=")
    .decode()
)


def _int_to_base64url(val: int) -> str:
    return (
        base64.urlsafe_b64encode(val.to_bytes((val.bit_length() + 7) // 8, "big"))
        .rstrip(b"=")
        .decode()
    )


e = _int_to_base64url(e_int)
JWKS_DOC = {
    "keys": [{"kty": "RSA", "alg": "RS256", "use": "sig", "n": n, "e": e, "kid": "0"}]
}


@router.get("/.well-known/jwks.json")
async def jwks():
    return JWKS_DOC
