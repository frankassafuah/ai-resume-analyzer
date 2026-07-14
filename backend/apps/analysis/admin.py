from django.contrib import admin

from apps.analysis.models import Analysis


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "status",
        "score",
        "ats_score",
        "provider",
        "model",
        "created_at",
    ]
    list_filter = ["status", "provider"]
    search_fields = ["user__email", "id"]
    readonly_fields = ["id", "created_at", "updated_at", "started_at", "completed_at"]
