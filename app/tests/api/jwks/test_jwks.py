import pytest

from fastapi.testclient import TestClient

from api.jwks import router

client = TestClient(router)


def test_jwks_endpoint():
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
