from config import config, DevConfig
from logging.config import dictConfig

def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(name)s:%(lineno)d - %(message)s"
                }
            },
            "handlers": {
                "default":{
                    # "class": "logging.StreamHandler",
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    "formatter": "console",
                }
            },
            "loggers": {
                "storeapi": {
                    "handler": ["defualt"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",\
                    "propagate": False,
                }
            }
        }
    )