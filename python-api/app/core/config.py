from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Event Monitoring API"
    database_url: str = "postgresql+psycopg2://postgres:postgres@postgres:5432/event_monitoring"
    internal_ingest_token: str = "local-token"
    burst_threshold_count: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_prefix="EMS_")


settings = Settings()
