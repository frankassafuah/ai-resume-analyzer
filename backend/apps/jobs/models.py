"""Models for job descriptions.

A `JobDescription` is a user-owned posting analyzed against resumes. It is
soft-deleted (recoverable) and separately *archivable* (kept but flagged
inactive), so a user's full history stays queryable.
"""
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from apps.common.models import SoftDeleteModel


class EmploymentType(models.TextChoices):
    FULL_TIME = "full_time", "Full-time"
    PART_TIME = "part_time", "Part-time"
    CONTRACT = "contract", "Contract"
    INTERNSHIP = "internship", "Internship"
    TEMPORARY = "temporary", "Temporary"
    FREELANCE = "freelance", "Freelance"


class JobDescription(SoftDeleteModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_descriptions"
    )
    company_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    description = models.TextField()
    required_skills = ArrayField(
        models.CharField(max_length=100), default=list, blank=True
    )
    location = models.CharField(max_length=255, blank=True)
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )

    is_archived = models.BooleanField(default=False, db_index=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    # Parsed requirements (populated by the AI pipeline later, M3/M4).
    parsed_json = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "jobs_job_description"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "is_archived"]),
        ]

    def __str__(self) -> str:
        return f"{self.job_title} @ {self.company_name}"

    def archive(self) -> None:
        if not self.is_archived:
            self.is_archived = True
            self.archived_at = timezone.now()
            self.save(update_fields=["is_archived", "archived_at", "updated_at"])

    def unarchive(self) -> None:
        if self.is_archived:
            self.is_archived = False
            self.archived_at = None
            self.save(update_fields=["is_archived", "archived_at", "updated_at"])
