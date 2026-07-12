from celery import shared_task


@shared_task(name="apps.common.tasks.ping")
def ping() -> str:
    """Trivial task proving the Celery/Redis round-trip works (M0 smoke test)."""
    return "pong"
