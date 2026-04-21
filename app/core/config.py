from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AutoParts Order & Analytics Platform"
    app_env: str = "dev"


settings = Settings()