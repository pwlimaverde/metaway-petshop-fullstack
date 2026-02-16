from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    metaway_petshop_docker_host: str = "ssh://user@host"
    docker_host: str = "ssh://user@host"
    compose_project_name: str = "metaway-petshop"

    app_env: str = "development"
    api_prefix: str = "/api/v1"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    web_port: int = 5173

    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_db: str = "metaway_petshop"
    postgres_user: str = "metaway_petshop"
    postgres_password: str = "change_me"
    database_url: str = (
        "postgresql+asyncpg://metaway_petshop:change_me@db:5432/metaway_petshop"
    )

    jwt_secret_key: str = "change_me_with_a_strong_secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    admin_seed_name: str = "Administrador"
    admin_seed_cpf: str = "00000000000"
    admin_seed_password: str = "change_me"

    upload_dir: str = "/app/storage"
    upload_max_size_mb: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()
