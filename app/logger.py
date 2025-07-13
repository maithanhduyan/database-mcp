# -*- coding: utf-8 -*-
# File: app/logger.py
# Logger for the application using Python's logging module.
# This module sets up a logger that writes logs to both a file and the console.
import logging
import logging.handlers
from queue import Queue

_log_queue = Queue(-1)
_listener_obj = None

# Unified logging configuration for uvicorn and application
UNIFIED_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(asctime)s - %(name)s - %(levelname)s - %(client_addr)s - "%(request_line)s" %(status_code)s',
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "file_handler": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "default",
            "level": "INFO",
            "encoding": "utf-8",
        },
        "console_handler": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO",
        },
        "access_file": {
            "class": "logging.FileHandler",
            "filename": "access.log",
            "formatter": "access",
            "level": "INFO",
            "encoding": "utf-8",
        },
        "access_console": {
            "class": "logging.StreamHandler",
            "formatter": "access",
            "level": "INFO",
        },
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["file_handler", "console_handler"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["file_handler", "console_handler"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["file_handler", "console_handler"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["access_file", "access_console"],
            "level": "INFO",
            "propagate": False,
        },
        "fastapi": {
            "handlers": ["file_handler", "console_handler"],
            "level": "INFO",
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "handlers": ["file_handler"],
            "level": "INFO",
            "propagate": False,
        },
        "app": {  # Application logger
            "handlers": ["file_handler", "console_handler"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Backwards compatibility
LOGGING_CONFIG = UNIFIED_LOGGING_CONFIG

from typing import Optional
import logging.config

def setup_unified_logging():
    """
    Set up unified logging configuration for uvicorn and application.
    This should be called once at application startup.
    """
    logging.config.dictConfig(UNIFIED_LOGGING_CONFIG)

def get_logger(name: Optional[str] = None):
    """
    Get a logger with the specified name. 
    Uses unified logging configuration that includes uvicorn and application logs.
    """
    global _listener_obj
    logger = logging.getLogger(name or __name__)
    
    # If unified logging is not set up, use QueueListener as fallback
    if not logging.getLogger().handlers:
        logger.setLevel(logging.INFO)
        if not any(isinstance(h, logging.handlers.QueueHandler) for h in logger.handlers):
            qh = logging.handlers.QueueHandler(_log_queue)
            logger.addHandler(qh)
            # Only set up the listener once
            if _listener_obj is None:
                file_handler = logging.FileHandler('app.log', encoding='utf-8')
                file_handler.setLevel(logging.INFO)
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                file_handler.setFormatter(formatter)
                console_handler.setFormatter(formatter)
                _listener_obj = logging.handlers.QueueListener(_log_queue, file_handler, console_handler)
                _listener_obj.start()
    
    return logger


def stop_logger():
    """
    Stop the QueueListener and flush all logs before exit.
    """
    global _listener_obj
    if _listener_obj is not None:
        _listener_obj.stop()
        _listener_obj = None

# Use this logger in your application like so:
# logger = get_logger(__name__)
