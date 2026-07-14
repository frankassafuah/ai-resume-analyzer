from django.contrib import admin

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["created_at", "user", "type", "title", "is_read", "emailed_at"]
    list_filter = ["type", "is_read"]
    search_fields = ["title", "message", "user__email"]
    readonly_fields = ["id", "created_at", "updated_at", "emailed_at"]
