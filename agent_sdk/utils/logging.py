"""
Structured logging utilities for Mnemosyne agents.

Provides consistent JSON-formatted logging across all agents with
contextual information for tracing and debugging.
"""

import logging
import sys
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

import json_log_formatter


class MnemosyneJSONFormatter(json_log_formatter.JSONFormatter):
    """Custom JSON formatter for Mnemosyne agents."""

    def json_record(
        self, message: str, extra: dict[str, Any], record: logging.LogRecord
    ) -> dict[str, Any]:
        """Create structured JSON log record."""
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        if extra:
            payload["context"] = extra

        if record.process:
            payload["process_id"] = record.process
        if record.thread:
            payload["thread_id"] = record.thread

        return payload


class ContextLogger(logging.LoggerAdapter):
    """Logger adapter that adds contextual information to all log messages."""

    def process(
        self, msg: str, kwargs: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """Add context to log message."""
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs


def setup_logger(
    name: str,
    level: int = logging.INFO,
    json_format: bool = True,
    context: Optional[dict[str, Any]] = None,
) -> ContextLogger:
    """Set up a logger for a Mnemosyne agent."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if json_format:
        formatter = MnemosyneJSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    context_logger = ContextLogger(logger, context or {})

    return context_logger


def get_logger(name: str) -> logging.Logger:
    """Get an existing logger by name."""
    return logging.getLogger(name)


def add_correlation_id(logger: ContextLogger, correlation_id: UUID) -> ContextLogger:
    """Add correlation ID to logger context."""
    new_context = logger.extra.copy()
    new_context["correlation_id"] = str(correlation_id)
    return ContextLogger(logger.logger, new_context)


def add_request_context(
    logger: ContextLogger, request_id: str, **kwargs: Any
) -> ContextLogger:
    """Add request-specific context to logger."""
    new_context = logger.extra.copy()
    new_context["request_id"] = request_id
    new_context.update(kwargs)
    return ContextLogger(logger.logger, new_context)


def log_event(
    logger: ContextLogger,
    event_type: str,
    message: str,
    **context: Any,
) -> None:
    """Log an event with standardized format."""
    context["event_type"] = event_type
    logger.info(message, extra=context)


def log_error(
    logger: ContextLogger,
    error: Exception,
    message: str,
    **context: Any,
) -> None:
    """Log an error with exception details."""
    context["error_type"] = type(error).__name__
    context["error_message"] = str(error)
    logger.error(message, exc_info=True, extra=context)


def log_performance(
    logger: ContextLogger,
    operation: str,
    duration_ms: float,
    **context: Any,
) -> None:
    """Log performance metrics for an operation."""
    context["operation"] = operation
    context["duration_ms"] = round(duration_ms, 2)
    logger.info(f"{operation} completed", extra=context)
