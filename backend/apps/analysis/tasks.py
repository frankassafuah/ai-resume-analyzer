"""Analysis Celery tasks (queue: analysis).

`run_analysis` executes a pending analysis and, on success or terminal failure,
enqueues the user notification. Transient failures (provider/network, or a
resume that isn't parsed yet) are retried with exponential backoff; once retries
are exhausted the analysis is marked FAILED and the user is still notified.
"""
import logging

from celery import shared_task
from django.conf import settings

from apps.ai.exceptions import ProviderError
from apps.analysis.services import AnalysisService
from apps.common.exceptions import ValidationError

logger = logging.getLogger("apps.analysis")


def _backoff(retries: int) -> int:
    # Exponential backoff (10s, 20s, 40s); instant under eager mode (tests/local).
    if settings.CELERY_TASK_ALWAYS_EAGER:
        return 0
    return 10 * (2 ** retries)

# Errors worth retrying: provider/network hiccups and "resume not parsed yet".
_RETRYABLE = (ProviderError, ValidationError)


@shared_task(
    bind=True,
    name="apps.analysis.tasks.run_analysis",
    max_retries=3,
    default_retry_delay=10,
)
def run_analysis(self, analysis_id: str) -> str:
    from apps.notifications.tasks import notify_analysis_complete

    service = AnalysisService()
    try:
        analysis = service.run(analysis_id)
    except _RETRYABLE as exc:
        if self.request.retries < self.max_retries:
            # Reschedule with exponential backoff (Celery re-runs the task).
            raise self.retry(exc=exc, countdown=_backoff(self.request.retries))  # noqa: B904
        # Retries exhausted -> terminal failure.
        logger.error("run_analysis %s exhausted retries: %s", analysis_id, exc)
        return _fail(service, analysis_id, exc, notify_analysis_complete)
    except Exception as exc:  # noqa: BLE001 — non-retryable: fail fast
        logger.exception("run_analysis %s failed", analysis_id)
        return _fail(service, analysis_id, exc, notify_analysis_complete)

    notify_analysis_complete.delay(str(analysis.id))
    return "completed"


def _fail(service, analysis_id, exc, notify) -> str:
    service.mark_failed(analysis_id, str(exc))
    notify.delay(analysis_id)
    return "failed"
