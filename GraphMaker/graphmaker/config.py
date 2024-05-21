from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file="/.env", env_file_encoding="utf-8")
    
    api_user: str = Field(env="API_USER", default="")
    api_pass: str = Field(env="API_PASS", default="")
    api_url: str = Field(env="API_URL", default="")
