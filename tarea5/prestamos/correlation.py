"""
Utilities for handling correlation IDs across the service.
Correlation IDs track requests through the system for logging and debugging.
"""

import logging
from flask import g


class CorrelationIdFilter(logging.Filter):
    """Filtro de logging para incluir el Correlation ID en cada mensaje de log."""

    def filter(self, record: logging.LogRecord) -> bool:
        # Agrega el Correlation ID al registro de log. Si no existe, usa "N/A".
        record.correlation_id = getattr(g, "correlation_id", "N/A")
        return True


def get_correlation_headers() -> dict:
    """
    Obtiene los headers necesarios para propagar el Correlation ID a servicios downstream.
    
    Returns:
        dict: Headers con el Correlation ID actual, o un header vacío si no está disponible.
    """
    correlation_id = getattr(g, "correlation_id", None)
    if correlation_id:
        return {"X-Correlation-ID": correlation_id}
    return {}
