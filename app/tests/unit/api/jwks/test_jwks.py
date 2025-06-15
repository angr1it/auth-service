"""Unit tests for JWKS endpoint."""

from fastapi.testclient import TestClient
import importlib


def test_jwks_endpoint():
    """Return JWKS with RSA key."""
    import api.jwks

    importlib.reload(api.jwks)
    client = TestClient(api.jwks.router)
    response = client.get("/.well-known/jwks.json")
    assert response.status_code == 200
    jwks = response.json()
    assert "keys" in jwks
    assert len(jwks["keys"]) > 0
    key = jwks["keys"][0]
    assert key["kty"] == "RSA"
    assert key["alg"] == "RS256"
    assert key["use"] == "sig"
    assert "n" in key
    assert "e" in key
    assert "kid" in key
