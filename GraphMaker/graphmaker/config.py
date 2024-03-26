from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    ch_host: str = Field(env="CH_HOST", default="")
    ch_port: int = Field(env="CH_PORT", default=0)
    ch_user: str = Field(env="CH_USER", default="")
    ch_pass: str = Field(env="CH_PASS", default="")
    base_url: str = Field(env="BASE_URL", default="https://cabinet.miem.hse.ru/public-api")