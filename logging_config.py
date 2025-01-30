import logging
from config import config, DevConfig
from logging.config import dictConfig

def obfuscated(email: str, obfuscated_length: int) -> str:
    # moha@gmail.com -> mo**@gmail.com
    characters = email[0:obfuscated_length]
    first, last = email.split("@")
    return characters + ("*" * (first) - obfuscated_length) + "@" + last

class EmailObfuscationFilter(logging.Filter):
    def __init__(self, name: str = "", obfuscated_length: int = 2) -> None:
        super().__init__(name)
        self.obfuscated_length = obfuscated_length
    def filter(self, record: logging.LogRecord) -> bool:
        if "email" in record.__dict__:
            record.email = obfuscated(record.email, self.obfuscated_length)
        return True
    
handlers = ["default", "rotating_file"]
if isinstance(config, DevConfig):
    handlers = ["default", "rotating_file", "logtail"]

def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": 8 if isinstance(config, DevConfig) else 32,
                    "default_value": "-"
                },
                "email_obfuscation": {
                    "()": EmailObfuscationFilter,
                    "obfuscated_length": 2 if isinstance(config, DevConfig) else 0,
                }
            },
           "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    # "format": "%(name)s:%(lineno)d - %(message)s"
                    "format": "(%(correlation_id)s) %(name)s:%(lineno)d - %(message)s"
                },
                "file": {
                    # "class": "logging.Formatter",
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(asctime).%(msecs)03d %(levelname)-8s (%(correlation_id)s) %(name)s %(lineno)d  %(message)s",
                    # "format": "%(asctime)s.%(msecs)03dZ | %(levelname)-8s, | [(%(correlation_id)s)] %(name)s:%(lineno)d - %(message)s"
                }
            },
            "handlers": {
                "default":{
                    # "class": "logging.StreamHandler",
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    "formatter": "console",
                    "filters": ["correlation_id", "email_obfuscation"]
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filename": "api.log",
                    "maxBytes": 1024 * 1024,
                    "backupCount": 5,
                    "encoding": "utf8",
                    "filters": ["correlation_id", "email_obfuscation"]
                },
                "logtail": {
                    "class": "logtail.LogtailHandler",
                    "level": "DEBUG",
                    "formatter": "console",
                    "filters": ["correlation_id"],
                    "source_token": config.LOGTAIL_API_KEY
                }
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["default", "rotating_file"], "level": "INFO",

                },
                "api": {
                    "handler": handlers,
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,
                },
                "databases": {
                    "handlers": ["default"], "level": "WARNING"
                }, 
                "aiosqlite": {
                    "handlers": ["default"], "level": "INFO"
                },
            }
        }
    )