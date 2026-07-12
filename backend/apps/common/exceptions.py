"""Application exceptions and the DRF exception handler.

Service-layer code raises the domain exceptions below; the handler converts any
DRF/domain error into the standard error envelope:

    {"success": false, "error": {"code": "...", "message": "...", "details": ...}}
"""
import logging
from typing import Any

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger("apps.common")


class ApplicationError(APIException):
    """Base class for domain errors. Subclasses set status_code + default_code."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "An application error occurred."
    default_code = "application_error"


class ValidationError(ApplicationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid input."
    default_code = "validation_error"


class NotFoundError(ApplicationError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found."
    default_code = "not_found"


class ConflictError(ApplicationError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Resource conflict."
    default_code = "conflict"


class PermissionDeniedError(ApplicationError):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have permission to perform this action."
    default_code = "permission_denied"


class QuotaExceededError(ApplicationError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "Usage quota exceeded."
    default_code = "quota_exceeded"


def _error_payload(code: str, message: Any, details: Any = None) -> dict:
    return {
        "success": False,
        "error": {"code": code, "message": message, "details": details},
    }


def custom_exception_handler(exc: Exception, context: dict) -> Response | None:
    # Normalize Django's own exceptions so DRF handles them uniformly.
    if isinstance(exc, Http404):
        exc = NotFoundError()
    elif isinstance(exc, DjangoPermissionDenied):
        exc = PermissionDeniedError()

    response = drf_exception_handler(exc, context)

    if response is None:
        # Unhandled -> 500. Log with stack; never leak internals to the client.
        logger.exception("Unhandled exception in %s", context.get("view"))
        return Response(
            _error_payload("server_error", "Internal server error."),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    code = getattr(exc, "default_code", "error")
    data = response.data
    # DRF puts the human message under "detail" for simple errors; validation
    # errors are a dict/list of field errors -> keep them as details.
    if isinstance(data, dict) and set(data.keys()) == {"detail"}:
        message, details = data["detail"], None
    else:
        message, details = response.status_text, data

    response.data = _error_payload(code, message, details)
    return response
