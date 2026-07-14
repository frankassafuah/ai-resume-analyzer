"""Service layer base.

Services hold business logic and orchestration (validation, permissions,
transactions, calling repositories / the AI gateway / dispatching Celery tasks).
Views stay thin: they parse input via serializers, call a service, and serialize
the result. Services never import DRF request/response objects.
"""
import logging


class BaseService:
    """Marker base for services; gives each service a namespaced logger."""

    def __init__(self) -> None:
        # __module__ already starts with "apps." (e.g. "apps.analysis.services"),
        # which sits under the configured "apps" logger namespace.
        self.logger = logging.getLogger(self.__class__.__module__)
