"""Pagination classes that emit the standard envelope.

Paginated responses look like:

    {
      "success": true,
      "data": [ ... ],
      "meta": {"pagination": {"count", "page", "pages", "page_size",
                              "next", "previous"}}
    }
"""
from collections import OrderedDict

from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework.response import Response


class DefaultPageNumberPagination(PageNumberPagination):
    """General-purpose pagination; client controls size via ?page_size=."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data) -> Response:
        return Response(
            {
                "success": True,
                "data": data,
                "meta": {
                    "pagination": {
                        "count": self.page.paginator.count,
                        "page": self.page.number,
                        "pages": self.page.paginator.num_pages,
                        "page_size": self.get_page_size(self.request),
                        "next": self.get_next_link(),
                        "previous": self.get_previous_link(),
                    }
                },
            }
        )


class TimeCursorPagination(CursorPagination):
    """Stable cursor pagination for large, time-ordered feeds (e.g. activity,
    notifications). Requires the queryset to have `created_at`."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
    ordering = "-created_at"

    def get_paginated_response(self, data) -> Response:
        return Response(
            OrderedDict(
                [
                    ("success", True),
                    ("data", data),
                    (
                        "meta",
                        {
                            "pagination": {
                                "next": self.get_next_link(),
                                "previous": self.get_previous_link(),
                                "page_size": self.get_page_size(self.request),
                            }
                        },
                    ),
                ]
            )
        )
