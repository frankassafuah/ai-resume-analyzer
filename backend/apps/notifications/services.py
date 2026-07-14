"""Notification service — create in-app notifications and send their email."""
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from apps.common.services import BaseService
from apps.notifications.models import Notification


class NotificationService(BaseService):
    def create(
        self, *, user, type: str, title: str, message: str = "", data: dict | None = None
    ) -> Notification:
        return Notification.objects.create(
            user=user, type=type, title=title, message=message, data=data or {}
        )

    def send_email(self, notification: Notification) -> None:
        """Send the notification as an email. Raises on failure so the calling
        Celery task can retry."""
        send_mail(
            subject=notification.title,
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.user.email],
            fail_silently=False,
        )
        notification.emailed_at = timezone.now()
        notification.save(update_fields=["emailed_at", "updated_at"])
        self.logger.info("Emailed notification %s to %s", notification.id, notification.user_id)
