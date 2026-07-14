"""User notifications (in-app record; email is sent alongside)."""
from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class Notification(BaseModel):
    class Type(models.TextChoices):
        ANALYSIS_COMPLETE = "analysis_complete", "Analysis complete"
        ANALYSIS_FAILED = "analysis_failed", "Analysis failed"
        SYSTEM = "system", "System"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(max_length=32, choices=Type.choices, default=Type.SYSTEM)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    # Arbitrary context, e.g. {"analysis_id": "...", "score": 90}.
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    emailed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "notifications_notification"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "is_read", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.type} -> {self.user_id}"
