
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "AirWatch API"
    api_prefix: str = "/api"
    database_url: str = "postgresql+psycopg://postgres:password@localhost:5432/airwatch"
    secret_key: str = "development-only-change-this-secret"
    access_token_expire_minutes: int = 1440
    frontend_origin: str = "http://localhost:5173"
    open_meteo_base_url: str = "https://air-quality-api.open-meteo.com/v1/air-quality"
    geocoding_base_url: str = "https://geocoding-api.open-meteo.com/v1/search"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
