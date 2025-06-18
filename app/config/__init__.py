from datetime import timedelta
from typing import Optional

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    auth_database_dsn: PostgresDsn
    echo_db_engine: Optional[bool] = True

    auth_jwt_private_key: str
    auth_jwt_public_key: str
    auth_jwt_algorithm: str

    access_token_ttl: Optional[timedelta] = timedelta(minutes=15)
    refresh_token_ttl: Optional[timedelta] = timedelta(days=14)

    cookie_domain: Optional[str] = "localhost"

    registration_token_url_prefix: Optional[str] = (
        "http://localhost:8000/api/v1/organization/register"
    )

    model_config = SettingsConfigDict(env_file=(".env"), extra="ignore")

    @field_validator("auth_jwt_private_key", "auth_jwt_public_key", mode="after")
    def _fix(cls, v):
        return v.replace("\\n", "\n")

app_settings = AppSettings()
print("App settings loaded successfully.")
print(app_settings.model_dump())
