"""Tests for logging configuration module."""

import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.utils.logging_config import (
    LoggingConfig,
    StructuredFormatter,
    clear_correlation_id,
    get_logger,
    set_correlation_id,
    setup_application_logging,
)


class TestStructuredFormatter:
    """Test structured JSON formatter."""

    def test_structured_formatter_init(self):
        """Test StructuredFormatter initialization."""
        formatter = StructuredFormatter()
        assert formatter.include_extra is True

        formatter_no_extra = StructuredFormatter(include_extra=False)
        assert formatter_no_extra.include_extra is False

    def test_structured_formatter_format_with_extra(self):
        """Test JSON formatting with extra fields."""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.event = "test_event"
        record.user_id = "123"

        result = formatter.format(record)
        import json

        parsed = json.loads(result)
        assert parsed["message"] == "Test message"
        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "test_logger"
        assert parsed["extra"]["event"] == "test_event"
        assert parsed["extra"]["user_id"] == "123"

    def test_structured_formatter_format_without_extra(self):
        """Test JSON formatting without extra fields."""
        formatter = StructuredFormatter(include_extra=False)
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        import json

        parsed = json.loads(result)
        assert parsed["message"] == "Test message"
        assert parsed["level"] == "INFO"
        assert "extra" not in parsed


class TestCorrelationTracking:
    """Test correlation ID tracking functionality."""

    def test_set_and_get_correlation_id(self):
        """Test setting and getting correlation ID."""
        test_id = "test-correlation-123"
        set_correlation_id(test_id)

        # Create a formatter to test correlation ID inclusion
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        import json

        parsed = json.loads(result)
        assert parsed["correlation_id"] == test_id

    def test_clear_correlation_id(self):
        """Test clearing correlation ID."""
        set_correlation_id("test-id")
        clear_correlation_id()

        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        import json

        parsed = json.loads(result)
        # After clearing, correlation_id should be null or not present
        assert parsed.get("correlation_id") is None


class TestLoggingConfig:
    """Test LoggingConfig class."""

    def test_logging_config_init_default(self):
        """Test LoggingConfig initialization with defaults."""
        with patch.dict(os.environ, {}, clear=True):
            config = LoggingConfig()
            assert config.app_name == "patient-risk-predictor"
            assert config.log_level == "INFO"
            assert config.environment == "local"
            assert not config.use_json_format  # Default for local environment

    def test_logging_config_init_with_env_vars(self):
        """Test LoggingConfig initialization with environment variables."""
        with patch.dict(
            os.environ,
            {
                "LOG_LEVEL": "DEBUG",
                "ENABLE_STRUCTURED_LOGGING": "false",
                "LOG_DIR": "/tmp/test-logs",
                "ENVIRONMENT": "development",
            },
        ):
            config = LoggingConfig("test-app")
            assert config.app_name == "test-app"
            assert config.log_level == "DEBUG"
            assert config.environment == "development"
            assert not config.use_json_format
            assert str(config.log_dir) == "/tmp/test-logs"

    def test_logging_config_with_yaml_file(self):
        """Test LoggingConfig with YAML configuration file."""
        yaml_content = """
version: 1
formatters:
  structured:
    format: "%(message)s"
handlers:
  console:
    class: logging.StreamHandler
loggers:
  test:
    level: WARNING
"""
        # Create a temporary yaml file and patch the config_file path
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name

        try:
            config = LoggingConfig()
            with patch.object(config, 'config_file', Path(yaml_path)):
                config._load_config_file()
                assert config.yaml_config is not None
                assert config.yaml_config["version"] == 1
        finally:
            os.unlink(yaml_path)

    def test_logging_config_with_invalid_yaml(self):
        """Test LoggingConfig with invalid YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            yaml_path = f.name

        try:
            config = LoggingConfig()
            with patch.object(config, 'config_file', Path(yaml_path)):
                config._load_config_file()
                assert config.yaml_config is None
        finally:
            os.unlink(yaml_path)

    def test_setup_logging_basic(self):
        """Test basic logging setup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"LOG_DIR": temp_dir}):
                config = LoggingConfig()
                logger = config.setup_logging()
                
                # Check that logger is configured
                assert isinstance(logger, logging.Logger)
                assert logger.name == "patient-risk-predictor"
                
                # Test logging works
                logger.info("Test info message")
                logger.error("Test error message")

    def test_setup_logging_json_format(self):
        """Test logging setup with JSON format."""
        with patch.dict(os.environ, {"ENABLE_STRUCTURED_LOGGING": "true"}):
            config = LoggingConfig()
            logger = config.setup_logging()
            
            # Should have JSON formatting enabled
            assert config.use_json_format
            assert isinstance(logger, logging.Logger)


class TestLoggingUtilities:
    """Test logging utility functions."""

    def test_get_logger(self):
        """Test get_logger function."""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "patient-risk-predictor.test_module"

    def test_setup_application_logging(self):
        """Test setup_application_logging function."""
        with patch.dict(os.environ, {"LOG_LEVEL": "WARNING"}):
            # Should not raise exception
            setup_application_logging()
            
            # Test that we can get a logger after setup
            logger = get_logger("test")
            assert isinstance(logger, logging.Logger)


class TestLoggingIntegration:
    """Integration tests for logging system."""

    def test_full_logging_workflow(self):
        """Test complete logging workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(
                os.environ,
                {
                    "LOG_TO_FILE": "true",
                    "LOG_DIR": temp_dir,
                    "LOG_LEVEL": "INFO",
                    "ENABLE_STRUCTURED_LOGGING": "true",
                },
            ):
                # Setup logging
                setup_application_logging()
                
                # Get logger and test correlation tracking
                logger = get_logger("test_module")
                set_correlation_id("test-correlation-123")
                
                # Log messages
                logger.info("Test message", extra={"event": "test_event"})
                logger.error("Test error", extra={"error_code": 500})
                
                clear_correlation_id()
                
                # Verify logger works
                assert logger.name == "patient-risk-predictor.test_module"

    def test_environment_specific_configuration(self):
        """Test that configuration adapts to different environments."""
        # Test development environment
        with patch.dict(
            os.environ, {"ENVIRONMENT": "development", "ENABLE_STRUCTURED_LOGGING": "false"}
        ):
            config = LoggingConfig()
            assert not config.use_json_format

        # Test production environment
        with patch.dict(
            os.environ, {"ENVIRONMENT": "production", "ENABLE_STRUCTURED_LOGGING": "true"}
        ):
            config = LoggingConfig()
            assert config.use_json_format