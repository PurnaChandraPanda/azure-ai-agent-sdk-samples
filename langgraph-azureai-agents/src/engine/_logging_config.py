
"""Module for configuring the logger."""
import logging
from logging import Logger
import sys


def configure_logger(name) -> Logger:
    """Configure and return a logger with the given name."""
    logger = logging.getLogger(name)

    ## To avoid duplicate logs, check if the logger already has handlers
    if logger.handlers:
        return logger

    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    format_str = "%(asctime)s [%(module)s] " ": %(levelname)-8s [%(process)d] %(message)s"
    formatter = logging.Formatter(format_str)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger