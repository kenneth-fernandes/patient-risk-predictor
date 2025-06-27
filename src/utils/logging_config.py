"""
Centralized logging configuration for the Patient Risk Predictor application.

This module provides structured logging with JSON formatting, request correlation,
and proper error tracking for better debugging and monitoring.
"""

import json
import logging
import logging.handlers
import os
import sys
import time
import uuid
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Dict, Optional

import yaml  # type: ignore

# Context variable for tracking request correlation IDs
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""

    def __init__(self, include_extra: bool = True):
        """
        Initialize the structured formatter.

        Args:
            include_extra: Whether to include extra fields in log output
        """
        super().__init__()
        self.include_extra = include_extra

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Base log structure
        log_data: Dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add correlation ID if available
        corr_id = correlation_id.get()
        if corr_id:
            log_data["correlation_id"] = corr_id

        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if record.exc_info else None,
            }

        # Add extra fields if enabled
        if self.include_extra:
            extra_fields = {
                key: value
                for key, value in record.__dict__.items()
                if key
                not in {
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "getMessage",
                }
            }
            if extra_fields:
                log_data["extra"] = extra_fields

        # Add environment and process info
        log_data["environment"] = os.getenv("ENVIRONMENT", "unknown")
        log_data["process_id"] = os.getpid()

        return json.dumps(log_data, default=str)


class LoggingConfig:
    """Centralized logging configuration manager."""

    def __init__(self, app_name: str = "patient-risk-predictor"):
        """
        Initialize logging configuration.

        Args:
            app_name: Name of the application for log identification
        """
        self.app_name = app_name

        # Configurable log directory
        log_dir_path = os.getenv("LOG_DIR", "logs")
        self.log_dir = Path(log_dir_path)
        self.log_dir.mkdir(exist_ok=True, parents=True)

        # Configuration based on environment
        self.environment = os.getenv("ENVIRONMENT", "local")
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.is_docker = os.getenv("DOCKER_CONTAINER") == "true" or os.path.exists("/.dockerenv")

        # Determine log format based on environment
        self.use_json_format = (
            self.environment in ["production", "docker"]
            or self.is_docker
            or os.getenv("ENABLE_STRUCTURED_LOGGING", "false").lower() == "true"
        )

        # Load configuration from YAML file
        self.config_file = Path("config/logging.yaml")
        self._load_config_file()

    def _load_config_file(self):
        """Load logging configuration from YAML file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    self.yaml_config = yaml.safe_load(f)
            except Exception as e:
                # Fallback to programmatic configuration if YAML loading fails
                print(f"Warning: Could not load logging config from {self.config_file}: {e}")
                self.yaml_config = None
        else:
            self.yaml_config = None

    def setup_logging(self) -> logging.Logger:
        """
        Setup and configure logging for the application.

        Returns:
            Configured root logger instance
        """
        # Clear any existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        # Set log level
        root_logger.setLevel(getattr(logging, self.log_level, logging.INFO))

        # Create formatters
        formatter: logging.Formatter
        if self.use_json_format:
            formatter = StructuredFormatter()
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, self.log_level, logging.INFO))
        root_logger.addHandler(console_handler)

        # File handler with rotation (only for local development or when explicitly enabled)
        enable_file_logging = (
            os.getenv("LOG_TO_FILE", "true" if not self.is_docker else "false").lower() == "true"
        )

        if enable_file_logging:
            # Ensure log directory exists
            self.log_dir.mkdir(exist_ok=True, parents=True)

            # Main log file handler
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / f"{self.app_name}.log",
                maxBytes=int(os.getenv("LOG_FILE_MAX_BYTES", "10485760")),  # Default 10MB
                backupCount=int(os.getenv("LOG_FILE_BACKUP_COUNT", "5")),  # Default 5 backups
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            root_logger.addHandler(file_handler)

            # Error-only file handler
            error_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / f"{self.app_name}-errors.log",
                maxBytes=int(os.getenv("LOG_ERROR_FILE_MAX_BYTES", "5242880")),  # Default 5MB
                backupCount=int(os.getenv("LOG_ERROR_FILE_BACKUP_COUNT", "3")),  # Default 3 backups
            )
            error_handler.setFormatter(formatter)
            error_handler.setLevel(logging.ERROR)
            root_logger.addHandler(error_handler)

        # Create application-specific logger
        app_logger = logging.getLogger(self.app_name)

        # Log the logging configuration
        app_logger.info(
            "Logging configured",
            extra={
                "event": "logging_setup_complete",
                "environment": self.environment,
                "log_level": self.log_level,
                "json_format": self.use_json_format,
                "is_docker": self.is_docker,
                "file_logging_enabled": enable_file_logging,
                "log_directory": str(self.log_dir.absolute())
                if enable_file_logging
                else "disabled",
            },
        )

        # Log application configuration if available
        try:
            from src.config import config

            app_logger.info(
                "Application configuration loaded",
                extra={"event": "config_debug_info", **config.get_debug_info()},
            )
        except ImportError:
            # Config not available during import
            pass

        return app_logger

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance for a specific module/component.

        Args:
            name: Name of the logger (typically __name__)

        Returns:
            Configured logger instance
        """
        return logging.getLogger(f"{self.app_name}.{name}")


def set_correlation_id(corr_id: Optional[str] = None) -> str:
    """
    Set correlation ID for request tracking.

    Args:
        corr_id: Correlation ID to set. If None, generates a new UUID.

    Returns:
        The correlation ID that was set
    """
    if corr_id is None:
        corr_id = str(uuid.uuid4())
    correlation_id.set(corr_id)
    return corr_id


def get_correlation_id() -> Optional[str]:
    """
    Get the current correlation ID.

    Returns:
        Current correlation ID or None if not set
    """
    return correlation_id.get()


def clear_correlation_id():
    """Clear the current correlation ID."""
    correlation_id.set(None)


# Global logging configuration instance
_logging_config = LoggingConfig()


def setup_application_logging() -> logging.Logger:
    """
    Setup logging for the entire application.

    Returns:
        Configured application logger
    """
    return _logging_config.setup_logging()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Configured logger instance
    """
    return _logging_config.get_logger(name)
