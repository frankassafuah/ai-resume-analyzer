"""Helpers for building standard success responses in custom (non-serializer)
endpoints. ViewSets get the envelope automatically via the renderer; use these
when you return a Response by hand."""
from typing import Any

from rest_framework import status as http_status
from rest_framework.response import Response


def success(data: Any = None, *, status: int = http_status.HTTP_200_OK,
            meta: dict | None = None) -> Response:
    payload: dict[str, Any] = {"success": True, "data": data}
    if meta is not None:
        payload["meta"] = meta
    return Response(payload, status=status)


def created(data: Any = None, *, meta: dict | None = None) -> Response:
    return success(data, status=http_status.HTTP_201_CREATED, meta=meta)


def no_content() -> Response:
    return Response(status=http_status.HTTP_204_NO_CONTENT)
