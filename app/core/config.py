from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Конфигурация приложения, загружаемая из переменных окружения.
    """

    project_name: str = "Ticket Service"
    database_url: str = Field(..., alias="DATABASE_URL")

    smtp_host: str = Field(..., alias="SMTP_HOST")
    smtp_port: int = Field(..., alias="SMTP_PORT")
    smtp_user: str = Field(..., alias="SMTP_USER")
    smtp_from: str = Field(..., alias="SMTP_FROM")
    smtp_password: str = Field(..., alias="SMTP_PASSWORD")

    secret_key: str = Field(..., alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, alias="refresh_token_expire_days")

    class Config:
        env_file = ".env"


settings = Settings()
