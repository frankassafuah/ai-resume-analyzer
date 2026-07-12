"""Standard success envelope.

All 2xx/3xx JSON responses are wrapped as:

    {"success": true, "data": <payload>}

Errors are already enveloped by `custom_exception_handler`, and paginated
responses by `DefaultPageNumberPagination` — both include a "success" key, so
this renderer passes them through untouched to avoid double-wrapping.
"""
from rest_framework.renderers import JSONRenderer


class StandardJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        response = renderer_context.get("response")

        already_enveloped = isinstance(data, dict) and "success" in data
        is_error = response is not None and response.status_code >= 400

        if not already_enveloped and not is_error:
            data = {"success": True, "data": data}

        return super().render(data, accepted_media_type, renderer_context)
