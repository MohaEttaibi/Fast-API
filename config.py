from pydantic import BaseSettings
from typing import Optional
from functools import lru_cache

class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None
    class Config:
        env_file: str = ".env"

class GlobalConfig(BaseSettings):
    DATABASE_URL = Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False

class DevConfig(GlobalConfig):
    class Config:
        env_prefix: str = "DEV_"


class TestConfig(GlobalConfig):
    DATABASE_URL = "sqlite:///test.db"
    DB_FORCE_ROLL_BACK: True
    class Config:
        env_prefix: str = "TEST_"


class ProdConfig(GlobalConfig):
    class Config:
        env_prefix: str = "PROD_"


@lru_cache
def get_config(env_state: str):
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    return configs[env_state]()

config = get_config(BaseConfig().ENV_STATE)