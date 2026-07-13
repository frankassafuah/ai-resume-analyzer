"""Models for resume upload, parsing, and versioning.

A `Resume` is the logical container a user owns; each upload creates a
`ResumeVersion` holding the actual file + (async) parsed output. `current_version`
points at the newest version. Resumes are soft-deleted (retained PII).
"""
import uuid

from django.conf import settings
from django.db import models

from apps.common.models import BaseModel, SoftDeleteModel


def resume_upload_path(instance: "ResumeVersion", filename: str) -> str:
    """Private, per-user, per-resume path. Never served via public MEDIA in prod;
    downloads go through an authenticated, owner-checked endpoint."""
    return (
        f"resumes/{instance.resume.user_id}/{instance.resume_id}/"
        f"{uuid.uuid4().hex}_{filename}"
    )


class Resume(SoftDeleteModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resumes"
    )
    title = models.CharField(max_length=255)
    current_version = models.ForeignKey(
        "ResumeVersion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        db_table = "resumes_resume"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.title} ({self.user_id})"

    @property
    def status(self) -> str:
        """Effective status derived from the current version."""
        return self.current_version.parse_status if self.current_version_id else "empty"


class ResumeVersion(BaseModel):
    class ParseStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PARSING = "parsing", "Parsing"
        PARSED = "parsed", "Parsed"
        FAILED = "failed", "Failed"

    resume = models.ForeignKey(
        Resume, on_delete=models.CASCADE, related_name="versions"
    )
    version = models.PositiveIntegerField()
    file = models.FileField(upload_to=resume_upload_path)
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10)  # "pdf" | "docx"
    size_bytes = models.PositiveIntegerField()

    parse_status = models.CharField(
        max_length=20, choices=ParseStatus.choices, default=ParseStatus.PENDING
    )
    parse_error = models.TextField(blank=True)
    parse_schema_version = models.CharField(max_length=20, blank=True)
    # Structured/extracted output (raw text now; AI-structured sections in M3/M4).
    parsed_json = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "resumes_resume_version"
        ordering = ["-version"]
        constraints = [
            models.UniqueConstraint(
                fields=["resume", "version"], name="uniq_resume_version"
            )
        ]

    def __str__(self) -> str:
        return f"{self.resume_id} v{self.version}"
