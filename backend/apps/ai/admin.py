from django.contrib import admin

from apps.ai.models import AIGenerationLog


@admin.register(AIGenerationLog)
class AIGenerationLogAdmin(admin.ModelAdmin):
    list_display = [
        "created_at",
        "provider",
        "model",
        "status",
        "tokens_in",
        "tokens_out",
        "cost_usd",
        "latency_ms",
        "user",
    ]
    list_filter = ["provider", "status", "model"]
    search_fields = ["model", "prompt_version", "user__email"]
    readonly_fields = [f.name for f in AIGenerationLog._meta.fields]

    def has_add_permission(self, request) -> bool:
        return False
