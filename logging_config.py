import logging
import logging.config

def setup_logging():
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.FileHandler",
                "level": "INFO",
                "formatter": "default",
                "filename": "app.log",
            },
        },
        "loggers": {
            "database_driver": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "recipe_manager": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "recipe_scraper": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "request_handler": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)