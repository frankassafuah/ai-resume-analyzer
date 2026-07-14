"""Analysis aggregate — one resume-vs-JD analysis run and its result.

Promoted, queryable columns (score, ats_score, status) sit alongside the full
AI payload in `result_json` (JSONB), versioned via `result_schema_version`
(ADR-0003). Snapshots of the analyzed text are stored so a result stays
reproducible even if the source resume/JD later changes.
"""
from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class Analysis(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="analyses"
    )
    # Optional links to the source records (analysis can also run on raw text).
    resume = models.ForeignKey(
        "resumes.Resume", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="analyses",
    )
    resume_version = models.ForeignKey(
        "resumes.ResumeVersion", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    job_description = models.ForeignKey(
        "jobs.JobDescription", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="analyses",
    )

    # Snapshots of exactly what was analyzed.
    resume_text = models.TextField()
    job_text = models.TextField()

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    provider = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=100, blank=True)
    prompt_version = models.CharField(max_length=50, blank=True)

    # Promoted, queryable metrics.
    score = models.PositiveSmallIntegerField(null=True, blank=True)
    ats_score = models.PositiveSmallIntegerField(null=True, blank=True)

    # Full AI payload.
    result_json = models.JSONField(null=True, blank=True)
    result_schema_version = models.CharField(max_length=50, blank=True)

    error = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "analysis_analysis"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]
        verbose_name_plural = "analyses"

    def __str__(self) -> str:
        return f"Analysis {self.id} [{self.status}]"
