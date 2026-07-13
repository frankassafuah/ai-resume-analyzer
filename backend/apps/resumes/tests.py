"""Resume management tests: upload, view, delete, download, versioning,
validation, and async parsing (run eagerly)."""
import io

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from docx import Document
from rest_framework.test import APIClient

from apps.resumes.models import Resume, ResumeVersion

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _settings(settings, tmp_path):
    # Isolate uploaded files and run the parse task inline.
    settings.MEDIA_ROOT = tmp_path
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True


@pytest.fixture
def user(db):
    return User.objects.create_user(email="u@example.com", password="Str0ng-Passw0rd!")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(email="o@example.com", password="Str0ng-Passw0rd!")


@pytest.fixture
def client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


# --- file fixtures --------------------------------------------------------
def docx_file(text="Jane Doe — Senior Engineer", name="resume.docx"):
    buf = io.BytesIO()
    doc = Document()
    doc.add_paragraph(text)
    doc.save(buf)
    return SimpleUploadedFile(
        name,
        buf.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


def pdf_file(name="resume.pdf"):
    # Minimal file with a valid PDF magic header (enough for upload validation).
    return SimpleUploadedFile(name, b"%PDF-1.4\n%%EOF\n", content_type="application/pdf")


LIST = "v1:resumes:resume-list"
DETAIL = "v1:resumes:resume-detail"
VERSIONS = "v1:resumes:resume-versions"
DOWNLOAD = "v1:resumes:resume-download"


# --- upload ---------------------------------------------------------------
def test_upload_docx_creates_resume_v1_and_parses(
    client, user, django_capture_on_commit_callbacks
):
    # Parsing is enqueued via transaction.on_commit; execute those callbacks so
    # the (eager) Celery task actually runs within the test transaction.
    with django_capture_on_commit_callbacks(execute=True):
        resp = client.post(reverse(LIST), {"file": docx_file(), "title": "My CV"},
                           format="multipart")
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["title"] == "My CV"
    assert data["current_version"]["version"] == 1

    resume = Resume.objects.get(id=data["id"])
    assert resume.user == user
    version = resume.current_version
    # Parsed eagerly by the Celery task.
    assert version.parse_status == ResumeVersion.ParseStatus.PARSED
    assert "Senior Engineer" in version.parsed_json["raw_text"]


def test_upload_defaults_title_from_filename(client):
    resp = client.post(reverse(LIST), {"file": docx_file(name="alice_cv.docx")},
                       format="multipart")
    assert resp.status_code == 201
    assert resp.json()["data"]["title"] == "alice_cv"


def test_upload_rejects_unsupported_extension(client):
    bad = SimpleUploadedFile("resume.txt", b"hello", content_type="text/plain")
    resp = client.post(reverse(LIST), {"file": bad}, format="multipart")
    assert resp.status_code == 400
    assert "file" in resp.json()["error"]["details"]


def test_upload_rejects_spoofed_content(client):
    # .pdf extension but not actually a PDF -> magic-byte check fails.
    fake = SimpleUploadedFile("evil.pdf", b"MZ\x90not a pdf",
                              content_type="application/pdf")
    resp = client.post(reverse(LIST), {"file": fake}, format="multipart")
    assert resp.status_code == 400


def test_upload_rejects_oversized_file(client, settings):
    settings.RESUME_MAX_UPLOAD_SIZE = 10  # 10 bytes
    resp = client.post(reverse(LIST), {"file": pdf_file()}, format="multipart")
    assert resp.status_code == 400


# --- view -----------------------------------------------------------------
def test_list_only_returns_own_resumes(client, user, other_user):
    client.post(reverse(LIST), {"file": docx_file()}, format="multipart")
    Resume.objects.create(user=other_user, title="theirs")

    resp = client.get(reverse(LIST))
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"] and all(r["title"] != "theirs" for r in body["data"])
    assert "pagination" in body["meta"]


def test_retrieve_other_users_resume_404(other_user):
    resume = Resume.objects.create(user=other_user, title="theirs")
    c = APIClient()
    c.force_authenticate(User.objects.create_user(email="x@e.com", password="Str0ng-Passw0rd!"))
    assert c.get(reverse(DETAIL, args=[resume.id])).status_code == 404


# --- versioning -----------------------------------------------------------
def test_add_version_increments_and_updates_current(client):
    created = client.post(reverse(LIST), {"file": docx_file()}, format="multipart").json()["data"]
    rid = created["id"]

    resp = client.post(reverse(VERSIONS, args=[rid]), {"file": docx_file(text="v2 content")},
                       format="multipart")
    assert resp.status_code == 201
    assert resp.json()["data"]["version"] == 2

    resume = Resume.objects.get(id=rid)
    assert resume.current_version.version == 2
    assert resume.versions.count() == 2


def test_list_versions(client):
    rid = client.post(reverse(LIST), {"file": docx_file()}, format="multipart").json()["data"]["id"]
    client.post(reverse(VERSIONS, args=[rid]), {"file": docx_file()}, format="multipart")
    resp = client.get(reverse(VERSIONS, args=[rid]))
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


# --- download -------------------------------------------------------------
def test_download_current_version(client):
    rid = client.post(reverse(LIST), {"file": docx_file()}, format="multipart").json()["data"]["id"]
    resp = client.get(reverse(DOWNLOAD, args=[rid]))
    assert resp.status_code == 200
    assert resp["Content-Disposition"].startswith("attachment")
    content = b"".join(resp.streaming_content)
    assert content[:2] == b"PK"  # docx is a zip


def test_download_requires_ownership(other_user):
    resume = Resume.objects.create(user=other_user, title="theirs")
    c = APIClient()
    c.force_authenticate(User.objects.create_user(email="y@e.com", password="Str0ng-Passw0rd!"))
    assert c.get(reverse(DOWNLOAD, args=[resume.id])).status_code == 404


# --- delete ---------------------------------------------------------------
def test_delete_is_soft(client):
    rid = client.post(reverse(LIST), {"file": docx_file()}, format="multipart").json()["data"]["id"]
    assert client.delete(reverse(DETAIL, args=[rid])).status_code == 204

    # Hidden from the API...
    assert client.get(reverse(DETAIL, args=[rid])).status_code == 404
    # ...but retained in the database (soft delete).
    assert Resume.all_objects.filter(id=rid, is_deleted=True).exists()


# --- auth -----------------------------------------------------------------
def test_upload_requires_auth():
    assert APIClient().post(reverse(LIST), {"file": docx_file()},
                            format="multipart").status_code == 401
