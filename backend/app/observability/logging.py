"""Structured JSON logging with correlation IDs."""
from __future__ import annotations

import logging
import sys
import uuid
from contextvars import ContextVar

import structlog

correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def set_correlation_id(cid: str | None) -> None:
    correlation_id.set(cid)


def get_correlation_id() -> str | None:
    return correlation_id.get()


def new_correlation_id() -> str:
    return str(uuid.uuid4())


class CorrelationIdProcessor:
    def __call__(self, logger, method_name, event_dict):
        cid = get_correlation_id()
        if cid:
            event_dict["correlation_id"] = cid
        return event_dict


def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            CorrelationIdProcessor(),
            structlog.processors.add_log_level,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "app"):
    return structlog.get_logger(name)
