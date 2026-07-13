"""Job description tests: CRUD, archive, history, filtering, search, pagination,
validation, and ownership isolation."""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.jobs.models import JobDescription

User = get_user_model()
pytestmark = pytest.mark.django_db

LIST = "v1:jobs:job-list"
DETAIL = "v1:jobs:job-detail"
ARCHIVE = "v1:jobs:job-archive"
UNARCHIVE = "v1:jobs:job-unarchive"


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


def payload(**over):
    data = {
        "company_name": "Acme Corp",
        "job_title": "Senior Python Engineer",
        "description": "We are looking for a backend engineer with Django experience.",
        "required_skills": ["Python", "Django", "PostgreSQL"],
        "location": "Remote",
        "employment_type": "full_time",
    }
    data.update(over)
    return data


def make_job(user, **over):
    fields = payload(**over)
    return JobDescription.objects.create(user=user, **fields)


# --- create ---------------------------------------------------------------
def test_create_job(client, user):
    resp = client.post(reverse(LIST), payload(), format="json")
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["company_name"] == "Acme Corp"
    assert data["required_skills"] == ["Python", "Django", "PostgreSQL"]
    assert data["employment_type_display"] == "Full-time"
    assert JobDescription.objects.filter(user=user).count() == 1


def test_create_normalizes_skills(client):
    resp = client.post(reverse(LIST),
                       payload(required_skills=[" Python ", "python", "Django", ""]),
                       format="json")
    assert resp.status_code == 201
    # trimmed, deduped (case-insensitive), blanks dropped
    assert resp.json()["data"]["required_skills"] == ["Python", "Django"]


def test_create_validation_errors(client):
    resp = client.post(reverse(LIST),
                       payload(company_name="", description="too short",
                               employment_type="bogus"),
                       format="json")
    assert resp.status_code == 400
    details = resp.json()["error"]["details"]
    assert "company_name" in details
    assert "description" in details
    assert "employment_type" in details


# --- edit -----------------------------------------------------------------
def test_update_job(client, user):
    job = make_job(user)
    resp = client.patch(reverse(DETAIL, args=[job.id]),
                       {"job_title": "Staff Engineer"}, format="json")
    assert resp.status_code == 200
    assert resp.json()["data"]["job_title"] == "Staff Engineer"
    job.refresh_from_db()
    assert job.job_title == "Staff Engineer"


# --- archive / history ----------------------------------------------------
def test_archive_and_unarchive(client, user):
    job = make_job(user)
    resp = client.post(reverse(ARCHIVE, args=[job.id]))
    assert resp.status_code == 200
    assert resp.json()["data"]["is_archived"] is True
    job.refresh_from_db()
    assert job.is_archived and job.archived_at is not None

    resp = client.post(reverse(UNARCHIVE, args=[job.id]))
    assert resp.json()["data"]["is_archived"] is False
    job.refresh_from_db()
    assert not job.is_archived and job.archived_at is None


def test_history_includes_archived_and_filter(client, user):
    make_job(user, job_title="Active Role")
    archived = make_job(user, job_title="Archived Role")
    archived.archive()

    # Full history (default) includes both.
    resp = client.get(reverse(LIST))
    titles = {j["job_title"] for j in resp.json()["data"]}
    assert {"Active Role", "Archived Role"} <= titles

    # Filter to archived only.
    resp = client.get(reverse(LIST), {"is_archived": "true"})
    got = [j["job_title"] for j in resp.json()["data"]]
    assert got == ["Archived Role"]


# --- delete (soft) --------------------------------------------------------
def test_delete_is_soft(client, user):
    job = make_job(user)
    assert client.delete(reverse(DETAIL, args=[job.id])).status_code == 204
    assert client.get(reverse(DETAIL, args=[job.id])).status_code == 404
    assert JobDescription.all_objects.filter(id=job.id, is_deleted=True).exists()


# --- filtering / search / pagination -------------------------------------
def test_filter_by_employment_type_and_skill(client, user):
    make_job(user, job_title="A", employment_type="full_time",
             required_skills=["Python", "AWS"])
    make_job(user, job_title="B", employment_type="contract",
             required_skills=["Go"])

    resp = client.get(reverse(LIST), {"employment_type": "contract"})
    assert [j["job_title"] for j in resp.json()["data"]] == ["B"]

    resp = client.get(reverse(LIST), {"skill": "AWS"})
    assert [j["job_title"] for j in resp.json()["data"]] == ["A"]


def test_search(client, user):
    make_job(user, job_title="Data Scientist", company_name="Netflix")
    make_job(user, job_title="Backend Engineer", company_name="Acme")
    resp = client.get(reverse(LIST), {"search": "netflix"})
    assert [j["job_title"] for j in resp.json()["data"]] == ["Data Scientist"]


def test_pagination(client, user):
    for i in range(25):
        make_job(user, job_title=f"Role {i}")
    resp = client.get(reverse(LIST), {"page_size": 10})
    body = resp.json()
    assert len(body["data"]) == 10
    assert body["meta"]["pagination"]["count"] == 25
    assert body["meta"]["pagination"]["pages"] == 3
    assert body["meta"]["pagination"]["next"] is not None


# --- ownership ------------------------------------------------------------
def test_cannot_access_others_job(other_user):
    job = make_job(other_user)
    c = APIClient()
    c.force_authenticate(User.objects.create_user(email="x@e.com", password="Str0ng-Passw0rd!"))
    assert c.get(reverse(DETAIL, args=[job.id])).status_code == 404
    assert c.patch(reverse(DETAIL, args=[job.id]), {"job_title": "hack"},
                   format="json").status_code == 404


def test_requires_auth():
    assert APIClient().get(reverse(LIST)).status_code == 401
