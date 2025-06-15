"""Unit tests for JWT helper functions."""

from fastapi import HTTPException
from core.jwt import helpers
from models.user import User


def _make_user() -> User:
    return User(id=1, organization_id="org", email="e", login="l", password_hash="h", perm_version=1)


def test_decode_access_token_valid(monkeypatch):
    """Decode valid token and return payload."""
    user = _make_user()
    token = helpers.issue_access_token(user)
    payload = helpers.decode_access_token(token)
    assert payload.sub == user.id
    assert payload.org == user.organization_id
    assert payload.login == user.login


def test_decode_access_token_expired(monkeypatch):
    """Expired token raises HTTPException."""
    user = _make_user()

    def past():
        import datetime as dt
        return dt.datetime.now(tz=dt.timezone.utc) - dt.timedelta(hours=1)

    monkeypatch.setattr(helpers, "_utc_now", past)
    token = helpers.issue_access_token(user)
    monkeypatch.setattr(helpers, "_utc_now", past)
    try:
        helpers.decode_access_token(token)
    except HTTPException as exc:
        assert exc.status_code == 401
    else:
        assert False, "Expected HTTPException"


def test_decode_access_token_wrong_key(monkeypatch):
    """Wrong signature results in HTTPException."""
    user = _make_user()
    token = helpers.issue_access_token(user)
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization

    other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pub = other.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    monkeypatch.setattr(helpers.app_settings, "auth_jwt_public_key", pub)
    try:
        helpers.decode_access_token(token)
    except HTTPException as exc:
        assert exc.status_code == 401
    else:
        assert False, "Expected HTTPException"


def test_issue_access_token_claims():
    """Issued token includes expected fields."""
    user = _make_user()
    token = helpers.issue_access_token(user)
    payload = helpers.decode_access_token(token)
    assert payload.pv == user.perm_version
    assert payload.jti
    assert payload.exp > payload.iat
