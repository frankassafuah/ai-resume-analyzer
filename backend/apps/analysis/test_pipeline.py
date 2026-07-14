"""Async pipeline tests: endpoint -> Celery tasks -> save -> notify.

Celery runs eagerly; on_commit callbacks are executed via
django_capture_on_commit_callbacks so the enqueue actually fires.
"""
import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.base import ContentFile
from django.urls import reverse
from rest_framework.test import APIClient

from apps.ai.exceptions import ProviderError
from apps.analysis.models import Analysis
from apps.jobs.models import JobDescription
from apps.notifications.models import Notification
from apps.resumes.models import Resume, ResumeVersion

User = get_user_model()
pytestmark = pytest.mark.django_db

CREATE = "v1:analysis:analysis-list"
DETAIL = "v1:analysis:analysis-detail"


@pytest.fixture(autouse=True)
def _settings(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True


@pytest.fixture
def user(db):
    return User.objects.create_user(email="u@example.com", password="Str0ng-Passw0rd!")


@pytest.fixture
def client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


def make_parsed_resume(user, text="Python Django AWS engineer"):
    resume = Resume.objects.create(user=user, title="CV")
    version = ResumeVersion.objects.create(
        resume=resume, version=1, file=ContentFile(b"x", name="cv.docx"),
        original_filename="cv.docx", file_type="docx", size_bytes=1,
        parse_status=ResumeVersion.ParseStatus.PARSED, parsed_json={"raw_text": text},
    )
    resume.current_version = version
    resume.save(update_fields=["current_version"])
    return resume


def make_job(user):
    return JobDescription.objects.create(
        user=user, company_name="Acme", job_title="Backend Engineer",
        description="Hiring a Python/Django engineer with Docker.",
        required_skills=["Python", "Django", "Docker"],
    )


# --- happy path -----------------------------------------------------------
def test_full_pipeline_completes_and_notifies(client, user, django_capture_on_commit_callbacks):
    resume, job = make_parsed_resume(user), make_job(user)

    with django_capture_on_commit_callbacks(execute=True):
        resp = client.post(reverse(CREATE),
                           {"resume_id": str(resume.id), "job_id": str(job.id)},
                           format="json")
    assert resp.status_code == 202
    analysis_id = resp.json()["data"]["id"]

    analysis = Analysis.objects.get(id=analysis_id)
    assert analysis.status == Analysis.Status.COMPLETED
    assert analysis.score is not None
    assert "python" in analysis.result_json["matching_skills"]

    # User notified: in-app record + email.
    note = Notification.objects.get(user=user, type=Notification.Type.ANALYSIS_COMPLETE)
    assert str(analysis.id) == note.data["analysis_id"]
    assert len(mail.outbox) == 1
    assert user.email in mail.outbox[0].to


def test_poll_status_via_detail(client, user, django_capture_on_commit_callbacks):
    resume, job = make_parsed_resume(user), make_job(user)
    with django_capture_on_commit_callbacks(execute=True):
        aid = client.post(reverse(CREATE),
                          {"resume_id": str(resume.id), "job_id": str(job.id)},
                          format="json").json()["data"]["id"]
    resp = client.get(reverse(DETAIL, args=[aid]))
    assert resp.status_code == 200
    body = resp.json()["data"]
    assert body["status"] == "completed" and body["result_json"]["summary"]


# --- ownership / validation ----------------------------------------------
def test_create_rejects_unowned_resume(client, user):
    other = User.objects.create_user(email="o@e.com", password="Str0ng-Passw0rd!")
    resume = make_parsed_resume(other)
    job = make_job(user)
    resp = client.post(reverse(CREATE),
                       {"resume_id": str(resume.id), "job_id": str(job.id)},
                       format="json")
    assert resp.status_code == 404


def test_create_requires_auth():
    assert APIClient().post(reverse(CREATE), {}, format="json").status_code == 401


# --- retry / failure handling --------------------------------------------
def test_pipeline_marks_failed_and_notifies_on_provider_error(
    client, user, monkeypatch, django_capture_on_commit_callbacks
):
    from apps.analysis.tasks import run_analysis

    # No retries -> the first provider failure is terminal (deterministic test).
    monkeypatch.setattr(run_analysis, "max_retries", 0)
    resume, job = make_parsed_resume(user), make_job(user)

    # Force the AI provider to always fail.
    from apps.ai.gateway import AIGateway

    def boom(self, *a, **k):
        raise ProviderError("provider down")

    monkeypatch.setattr(AIGateway, "complete", boom)

    with django_capture_on_commit_callbacks(execute=True):
        aid = client.post(reverse(CREATE),
                          {"resume_id": str(resume.id), "job_id": str(job.id)},
                          format="json").json()["data"]["id"]

    analysis = Analysis.objects.get(id=aid)
    assert analysis.status == Analysis.Status.FAILED
    assert "provider down" in analysis.error
    # Still notified (failure notification).
    assert Notification.objects.filter(
        user=user, type=Notification.Type.ANALYSIS_FAILED
    ).exists()


def test_run_analysis_retries_on_transient(monkeypatch):
    """A transient ProviderError schedules a retry (raises Celery Retry)."""
    from celery.exceptions import Retry

    from apps.analysis import tasks
    from apps.analysis.services import AnalysisService

    def flaky_run(self, analysis_id):
        raise ProviderError("temporary")

    monkeypatch.setattr(AnalysisService, "run", flaky_run)
    with pytest.raises(Retry):
        tasks.run_analysis.apply(args=["some-id"], throw=True)
