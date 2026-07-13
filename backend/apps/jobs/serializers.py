"""Serializers for job descriptions.

Read/write split: the write serializer validates and normalizes input (trims
strings, dedupes/cleans skills); the read serializer shapes responses.
"""
from rest_framework import serializers

from apps.jobs.models import EmploymentType, JobDescription


class JobDescriptionSerializer(serializers.ModelSerializer):
    """Response representation."""

    employment_type_display = serializers.CharField(
        source="get_employment_type_display", read_only=True
    )

    class Meta:
        model = JobDescription
        fields = [
            "id",
            "company_name",
            "job_title",
            "description",
            "required_skills",
            "location",
            "employment_type",
            "employment_type_display",
            "is_archived",
            "archived_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class JobDescriptionWriteSerializer(serializers.ModelSerializer):
    """Create/update payload validation."""

    required_skills = serializers.ListField(
        # Blanks are allowed through then dropped in validate_required_skills,
        # so a stray "" in the list doesn't 400 the whole request.
        child=serializers.CharField(max_length=100, allow_blank=True),
        required=False,
        default=list,
    )

    class Meta:
        model = JobDescription
        fields = [
            "company_name",
            "job_title",
            "description",
            "required_skills",
            "location",
            "employment_type",
        ]

    def validate_company_name(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Company name is required.")
        return value

    def validate_job_title(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Job title is required.")
        return value

    def validate_description(self, value: str) -> str:
        value = value.strip()
        if len(value) < 20:
            raise serializers.ValidationError(
                "Description must be at least 20 characters."
            )
        return value

    def validate_employment_type(self, value: str) -> str:
        if value not in EmploymentType.values:
            raise serializers.ValidationError("Invalid employment type.")
        return value

    def validate_required_skills(self, value: list[str]) -> list[str]:
        # Trim, drop blanks, dedupe (case-insensitive, first spelling wins).
        seen: set[str] = set()
        cleaned: list[str] = []
        for skill in value:
            s = skill.strip()
            if s and s.lower() not in seen:
                seen.add(s.lower())
                cleaned.append(s)
        return cleaned
