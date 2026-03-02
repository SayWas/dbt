from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_env: str = "dev"
    app_request_timeout: int = 15

    aviasales_base_url: str = "https://api.travelpayouts.com/aviasales/v3"
    aviasales_api_token: str = "replace_me"
    default_origins: str = "SVO,DME,VKO"
    default_destinations: str = "LED,IST,DXB"
    default_days_ahead: int = 90

    mongo_host: str = "mongodb"
    mongo_port: int = 27017
    mongo_db: str = "airfares"
    mongo_user: str = "root"
    mongo_password: str = "root"
    mongo_auth_db: str = "admin"
    mongo_collection: str = "raw_flight_prices"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @property
    def mongo_uri(self) -> str:
        return (
            f"mongodb://{self.mongo_user}:{self.mongo_password}"
            f"@{self.mongo_host}:{self.mongo_port}/"
            f"?authSource={self.mongo_auth_db}"
        )


settings = Settings()
