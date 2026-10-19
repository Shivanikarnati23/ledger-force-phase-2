from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://user:password@db:5432/ledger_db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()