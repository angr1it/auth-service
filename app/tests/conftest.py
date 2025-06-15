"""Common test fixtures."""

import importlib
from typing import Generator

import models
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from config import app_settings


@pytest.fixture(autouse=True)
def jwt_keys() -> Generator[None, None, None]:
    """Generate ephemeral RSA keys for tests."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    priv_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    pub_pem = (
        private_key.public_key()
        .public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )

    app_settings.auth_jwt_private_key = priv_pem
    app_settings.auth_jwt_public_key = pub_pem
    app_settings.auth_jwt_algorithm = "RS256"

    import api.jwks

    importlib.reload(api.jwks)
    yield
