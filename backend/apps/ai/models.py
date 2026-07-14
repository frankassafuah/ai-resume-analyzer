"""AI persistence: a log of every LLM generation for cost/latency/audit.

The provider gateway writes one row per call — provider, model, prompt version,
tokens, cost, latency, and outcome — so usage is fully auditable and
reproducible regardless of which provider produced a result.
"""
from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class AIGenerationLog(BaseModel):
    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ai_generation_logs",
    )
    analysis = models.ForeignKey(
        "analysis.Analysis",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="generation_logs",
    )
    provider = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    prompt_version = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices)
    tokens_in = models.PositiveIntegerField(default=0)
    tokens_out = models.PositiveIntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    latency_ms = models.PositiveIntegerField(default=0)
    error = models.TextField(blank=True)

    class Meta:
        db_table = "ai_generation_log"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["-created_at"])]

    def __str__(self) -> str:
        return f"{self.provider}/{self.model} [{self.status}]"
