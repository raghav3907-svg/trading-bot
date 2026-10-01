"""
Centralized logging configuration for the trading bot.

Logs go to both the console (INFO+) and a rotating log file (DEBUG+),
so every API request, response, and error is captured for the
deliverable log files required by the assignment.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE = os.path.join("/tmp", "trading_bot.log") if os.getenv("VERCEL") else os.path.join(LOG_DIR, "trading_bot.log")


def setup_logging(log_file: str = LOG_FILE, level: int = logging.DEBUG) -> logging.Logger:
    """Configure and return the root 'trading_bot' logger."""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger("trading_bot")
    logger.setLevel(level)
    logger.propagate = False

    if logger.handlers:
        # Avoid duplicate handlers if setup_logging() is called more than once
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rotating file handler: keeps logs from growing unbounded
    file_handler = RotatingFileHandler(
        log_file, maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler: only show INFO+ so the CLI output stays clean
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
