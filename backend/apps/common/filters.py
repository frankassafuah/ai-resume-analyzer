"""Filtering conventions built on django-filter.

Domain apps define `class FooFilter(BaseFilterSet)` with explicit fields, then
set `filterset_class = FooFilter` on the viewset. `BaseFilterSet` adds a common
created-at range filter that every timestamped model can use.
"""
from django_filters import rest_framework as df


class BaseFilterSet(df.FilterSet):
    created_after = df.IsoDateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = df.IsoDateTimeFilter(field_name="created_at", lookup_expr="lte")
