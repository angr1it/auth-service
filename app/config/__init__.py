from datetime import timedelta
from typing import Optional

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    database_dsn: PostgresDsn
    echo_db_engine: Optional[bool] = True

    jwt_private_key: str
    jwt_public_key: str
    jwt_algorithm: str

    access_token_ttl: Optional[timedelta] = timedelta(minutes=15)
    refresh_token_ttl: Optional[timedelta] = timedelta(days=14)

    cookie_domain: Optional[str] = "localhost"

    registration_token_url_prefix: Optional[str] = "http://localhost:8000/api/v1/organization/register"

    model_config = SettingsConfigDict(env_file=(".env"), extra="ignore")


app_settings = AppSettings()
