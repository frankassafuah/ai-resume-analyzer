import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("ai_resume_analyzer")

# All Celery config lives in Django settings under the CELERY_ namespace.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Discover tasks.py modules across installed apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self) -> None:
    print(f"Request: {self.request!r}")
