from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    api_prefix: str = "/api/v1"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_db: str = "metaway_petshop"
    postgres_user: str = "metaway_petshop"
    postgres_password: str
    database_url: str | None = None

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    admin_seed_name: str = "Administrador"
    admin_seed_cpf: str = "52998224725"
    admin_seed_password: str
    run_seed_on_startup: bool = False

    upload_dir: str = "/app/storage"
    upload_max_size_mb: int = 5

    @model_validator(mode="after")
    def assemble_database_url(self) -> "Settings":
        if self.database_url is None:
            self.database_url = (
                f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
