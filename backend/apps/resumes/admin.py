from django.contrib import admin

from apps.resumes.models import Resume, ResumeVersion


class ResumeVersionInline(admin.TabularInline):
    model = ResumeVersion
    extra = 0
    fields = ["version", "file_type", "size_bytes", "parse_status", "created_at"]
    readonly_fields = fields
    show_change_link = True


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "status", "is_deleted", "created_at"]
    list_filter = ["is_deleted", "created_at"]
    search_fields = ["title", "user__email"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [ResumeVersionInline]


@admin.register(ResumeVersion)
class ResumeVersionAdmin(admin.ModelAdmin):
    list_display = ["resume", "version", "file_type", "parse_status", "created_at"]
    list_filter = ["parse_status", "file_type"]
    readonly_fields = ["id", "created_at", "updated_at"]
