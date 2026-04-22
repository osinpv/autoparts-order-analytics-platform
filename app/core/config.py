from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AutoParts Order & Analytics Platform"
    app_env: str = "dev"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "autoparts_db"
    postgres_user: str = "autoparts_user"
    postgres_password: str = "autoparts_pass"

    database_url: str = (
        "postgresql+psycopg://autoparts_user:autoparts_pass@localhost:5432/autoparts_db"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()