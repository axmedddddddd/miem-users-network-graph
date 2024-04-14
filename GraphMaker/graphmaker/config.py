from pydantic_settings import BaseSettings
from pydantic import Field
import os

class BaseConfig(BaseSettings):
    ch_host: str = Field(default="", env="CH_HOST")
    ch_port: str = Field(default="", env="CH_PORT")
    ch_user: str = Field(default="", env="CH_USER")
    ch_pass: str = Field(default="", env="CH_PASS")
    base_url: str = Field(default="https://cabinet.miem.hse.ru/public-api", env="BASE_URL")

    class Config:
        env_file = "/code/graphmaker/.env"
        env_file_encoding = "utf-8"
