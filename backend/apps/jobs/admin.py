from django.contrib import admin

from apps.jobs.models import JobDescription


@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = [
        "job_title",
        "company_name",
        "employment_type",
        "user",
        "is_archived",
        "is_deleted",
        "created_at",
    ]
    list_filter = ["employment_type", "is_archived", "is_deleted", "created_at"]
    search_fields = ["job_title", "company_name", "description", "user__email"]
    readonly_fields = ["id", "created_at", "updated_at", "archived_at"]
