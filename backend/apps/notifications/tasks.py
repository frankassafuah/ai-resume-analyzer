"""Notification Celery tasks (queue: notifications).

Email delivery is retried with exponential backoff — transient SMTP failures
shouldn't lose a user notification. The in-app Notification row is created first
(synchronously in the calling flow), so a failed email never means a lost record.
"""
import logging

from celery import shared_task

from apps.notifications.models import Notification
from apps.notifications.services import NotificationService

logger = logging.getLogger("apps.notifications")


@shared_task(
    bind=True,
    name="apps.notifications.tasks.send_notification_email",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    max_retries=5,
)
def send_notification_email(self, notification_id: str) -> str:
    try:
        notification = Notification.objects.select_related("user").get(pk=notification_id)
    except Notification.DoesNotExist:
        logger.warning("send_notification_email: %s not found", notification_id)
        return "not_found"

    NotificationService().send_email(notification)
    return "sent"


@shared_task(name="apps.notifications.tasks.notify_analysis_complete")
def notify_analysis_complete(analysis_id: str) -> str:
    """Create the in-app notification for a finished analysis and enqueue its
    email. Kept separate from run_analysis so notification failures never affect
    the analysis result."""
    from apps.analysis.models import Analysis  # local import avoids app cycles

    try:
        analysis = Analysis.objects.select_related("user").get(pk=analysis_id)
    except Analysis.DoesNotExist:
        logger.warning("notify_analysis_complete: analysis %s not found", analysis_id)
        return "not_found"

    service = NotificationService()
    if analysis.status == Analysis.Status.COMPLETED:
        note = service.create(
            user=analysis.user,
            type=Notification.Type.ANALYSIS_COMPLETE,
            title="Your resume analysis is ready",
            message=(
                f"Your analysis is complete with a match score of {analysis.score}% "
                f"(ATS {analysis.ats_score}%)."
            ),
            data={"analysis_id": str(analysis.id), "score": analysis.score},
        )
    else:
        note = service.create(
            user=analysis.user,
            type=Notification.Type.ANALYSIS_FAILED,
            title="Your resume analysis could not be completed",
            message="Something went wrong analyzing your resume. Please try again.",
            data={"analysis_id": str(analysis.id)},
        )

    send_notification_email.delay(str(note.id))
    return "notified"
