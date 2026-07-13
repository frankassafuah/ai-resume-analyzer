"""Filters for job descriptions."""
from django_filters import rest_framework as df

from apps.common.filters import BaseFilterSet
from apps.jobs.models import EmploymentType, JobDescription


class JobDescriptionFilter(BaseFilterSet):
    employment_type = df.ChoiceFilter(choices=EmploymentType.choices)
    company = df.CharFilter(field_name="company_name", lookup_expr="icontains")
    location = df.CharFilter(lookup_expr="icontains")
    is_archived = df.BooleanFilter()
    # ?skill=python -> jobs whose required_skills array contains "python"
    skill = df.CharFilter(method="filter_skill")

    class Meta:
        model = JobDescription
        fields = ["employment_type", "is_archived", "company", "location", "skill"]

    def filter_skill(self, queryset, name, value):
        return queryset.filter(required_skills__contains=[value])
