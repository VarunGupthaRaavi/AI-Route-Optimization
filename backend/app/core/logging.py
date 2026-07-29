import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict
from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """
    Custom Log Formatter emitting structured JSON logs for observability platforms
    (e.g., Render Logs, Datadog, ELK stack).
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats python log records into a structured JSON string.
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "environment": settings.ENVIRONMENT,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Contextual metadata attached to record extra
        if hasattr(record, "request_id"):
            log_data["request_id"] = getattr(record, "request_id")
        if hasattr(record, "process_time_ms"):
            log_data["process_time_ms"] = getattr(record, "process_time_ms")

        # Include exception tracebacks if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging() -> logging.Logger:
    """
    Initializes global application logging based on project configuration settings.
    Configures root logger handlers and levels for console or production JSON output.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear pre-existing log handlers to prevent duplication
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    if settings.LOG_FORMAT.lower() == "json":
        formatter: logging.Formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Suppress verbose noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DB_ECHO else logging.WARNING
    )

    logger = logging.getLogger("routeai")
    logger.info(f"Logging initialized in [{settings.ENVIRONMENT}] mode with level [{settings.LOG_LEVEL}]")
    return logger


logger = setup_logging()
