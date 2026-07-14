"""Analysis service tests: running an analysis and persisting the result."""
import pytest
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from apps.ai.models import AIGenerationLog
from apps.analysis.models import Analysis
from apps.analysis.services import AnalysisService
from apps.common.exceptions import ValidationError
from apps.jobs.models import JobDescription
from apps.resumes.models import Resume, ResumeVersion

User = get_user_model()
pytestmark = pytest.mark.django_db

RESUME = "Backend engineer skilled in Python, Django, PostgreSQL, Redis."
JOB = "Hiring a Python/Django engineer; Docker experience preferred."


@pytest.fixture(autouse=True)
def _media(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


@pytest.fixture
def user(db):
    return User.objects.create_user(email="a@example.com", password="Str0ng-Passw0rd!")


def test_analyze_persists_completed_result(user):
    analysis = AnalysisService().analyze(
        user=user, resume_text=RESUME, job_text=JOB
    )
    assert analysis.status == Analysis.Status.COMPLETED
    assert analysis.score is not None and 0 <= analysis.score <= 100
    assert analysis.result_json["matching_skills"]  # populated
    assert "python" in analysis.result_json["matching_skills"]
    assert analysis.provider == "fake"
    assert analysis.completed_at is not None

    # The generation was logged and linked to this analysis.
    log = AIGenerationLog.objects.get(analysis=analysis)
    assert log.status == "success"


def test_analyze_requires_both_texts(user):
    with pytest.raises(ValidationError):
        AnalysisService().analyze(user=user, resume_text="  ", job_text=JOB)


def test_analyze_resume_pulls_parsed_text(user):
    resume = Resume.objects.create(user=user, title="CV")
    version = ResumeVersion.objects.create(
        resume=resume,
        version=1,
        file=ContentFile(b"x", name="cv.docx"),
        original_filename="cv.docx",
        file_type="docx",
        size_bytes=1,
        parse_status=ResumeVersion.ParseStatus.PARSED,
        parsed_json={"raw_text": RESUME},
    )
    resume.current_version = version
    resume.save(update_fields=["current_version"])

    job = JobDescription.objects.create(
        user=user, company_name="Acme", job_title="Backend Engineer",
        description=JOB, required_skills=["Python", "Django"],
    )

    analysis = AnalysisService().analyze_resume(user=user, resume=resume, job=job)
    assert analysis.status == Analysis.Status.COMPLETED
    assert analysis.resume_id == resume.id
    assert analysis.job_description_id == job.id
    assert "python" in analysis.result_json["matching_skills"]


def test_analyze_resume_requires_parsed_text(user):
    resume = Resume.objects.create(user=user, title="CV")
    version = ResumeVersion.objects.create(
        resume=resume, version=1, file=ContentFile(b"x", name="cv.pdf"),
        original_filename="cv.pdf", file_type="pdf", size_bytes=1,
    )
    resume.current_version = version
    resume.save(update_fields=["current_version"])
    job = JobDescription.objects.create(
        user=user, company_name="Acme", job_title="Eng", description=JOB,
    )
    with pytest.raises(ValidationError):
        AnalysisService().analyze_resume(user=user, resume=resume, job=job)
