"""Seed the database with demo data covering every scenario.

Idempotent: wipes the demo users (and their cascade) then recreates everything —
so `python manage.py seed` can be re-run any time.

Covers:
  - resumes in every parse state (parsed, pending, parsing, failed) + versioning
  - job descriptions across employment types, with/without skills, archived
  - analyses in every status (completed high/mid/low, processing, pending, failed)
  - notifications (complete/failed/system, read + unread)
  - AI generation logs (success + error)
  - a second user, to prove ownership isolation
"""
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.ai.models import AIGenerationLog
from apps.analysis.models import Analysis
from apps.jobs.models import EmploymentType, JobDescription
from apps.notifications.models import Notification
from apps.resumes.models import Resume, ResumeVersion

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "Demo1234!"
OTHER_EMAIL = "other@example.com"

RESUME_TEXT = (
    "Jane Doe\nSenior Python Engineer\n\n"
    "Experience: 8 years building backend systems with Python, Django, "
    "PostgreSQL, Redis, Celery and AWS. Led a team of 5 engineers. "
    "Designed REST APIs and event-driven pipelines.\n"
    "Skills: Python, Django, PostgreSQL, Redis, Celery, AWS, Docker, REST.\n"
    "Education: BSc Computer Science."
)


def make_docx(text: str, name: str) -> ContentFile:
    from docx import Document

    buf = BytesIO()
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    doc.save(buf)
    return ContentFile(buf.getvalue(), name=name)


def make_pdf(name: str) -> ContentFile:
    # Minimal valid-header PDF (enough for storage/download in a demo).
    return ContentFile(b"%PDF-1.4\n%demo seed file\n%%EOF\n", name=name)


def result(score: int, ats: int, matching, missing) -> dict:
    return {
        "score": score,
        "ats_score": ats,
        "matching_skills": matching,
        "missing_skills": missing,
        "keywords": matching[:6],
        "strengths": [
            "Strong backend fundamentals with production experience.",
            "Clear, ATS-readable structure and formatting.",
            "Demonstrated leadership and ownership.",
        ],
        "weaknesses": [
            "Limited exposure to some required tools.",
            "Few quantified achievements (metrics/impact).",
        ],
        "summary": (
            f"Candidate matches roughly {score}% of the role. Solid overlap on "
            "core skills; a few targeted additions would strengthen the fit."
        ),
        "recommendations": [
            "Add measurable achievements (numbers, %, scale).",
            f"Highlight or gain experience with {', '.join(missing) or 'the listed tools'}.",
            "Mirror the exact keywords from the job description.",
        ],
    }


class Command(BaseCommand):
    help = "Seed the database with comprehensive demo data (idempotent)."

    @transaction.atomic
    def handle(self, *args, **options):
        self._wipe()
        demo = self._user(DEMO_EMAIL, "Jane", "Doe")
        other = self._user(OTHER_EMAIL, "Other", "User")

        resumes = self._resumes(demo)
        jobs = self._jobs(demo)
        self._analyses(demo, resumes, jobs)
        self._notifications(demo)

        # Ownership-isolation user: their own data must never show for demo.
        r = Resume.objects.create(user=other, title="Other User CV")
        v = ResumeVersion.objects.create(
            resume=r, version=1, file=make_docx("Other user resume", "other.docx"),
            original_filename="other.docx", file_type="docx", size_bytes=100,
            parse_status=ResumeVersion.ParseStatus.PARSED, parsed_json={"raw_text": "x"},
        )
        r.current_version = v
        r.save(update_fields=["current_version"])
        JobDescription.objects.create(
            user=other, company_name="OtherCo", job_title="Other Role",
            description="Other role description that is long enough.", required_skills=["Go"],
        )

        self.stdout.write(self.style.SUCCESS("\n✔ Seed complete."))
        self.stdout.write(
            f"  Demo login: {DEMO_EMAIL} / {DEMO_PASSWORD}\n"
            f"  Resumes: {Resume.objects.filter(user=demo).count()} · "
            f"Jobs: {JobDescription.objects.filter(user=demo).count()} · "
            f"Analyses: {Analysis.objects.filter(user=demo).count()} · "
            f"Notifications: {Notification.objects.filter(user=demo).count()}"
        )

    # --- helpers ----------------------------------------------------------
    def _wipe(self):
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

        emails = [DEMO_EMAIL, OTHER_EMAIL]
        OutstandingToken.objects.filter(user__email__in=emails).delete()
        User.objects.filter(email__in=emails).delete()
        self.stdout.write("• Wiped existing demo users")

    def _user(self, email: str, first: str, last: str) -> User:
        return User.objects.create_user(
            email=email, password=DEMO_PASSWORD, first_name=first, last_name=last,
            email_verified=True,
        )

    def _resumes(self, user) -> dict:
        # 1) Parsed resume with TWO versions (versioning scenario).
        parsed = Resume.objects.create(user=user, title="Senior Python Engineer CV")
        self._version(parsed, 1, RESUME_TEXT, "cv_v1.docx", "docx", parsed=True)
        v2 = self._version(parsed, 2, RESUME_TEXT + "\nAdded: GraphQL, Kubernetes.",
                           "cv_v2.docx", "docx", parsed=True)
        parsed.current_version = v2
        parsed.save(update_fields=["current_version"])

        # 2) Parsed PDF resume.
        pdf_resume = Resume.objects.create(user=user, title="Frontend Developer Resume")
        pv = self._version(
            pdf_resume, 1,
            "React, TypeScript, Tailwind, Vue, Vite frontend engineer.",
            "frontend.pdf", "pdf", parsed=True, pdf=True,
        )
        pdf_resume.current_version = pv
        pdf_resume.save(update_fields=["current_version"])

        # 3) Pending (uploaded, not parsed yet).
        pending = Resume.objects.create(user=user, title="Data Scientist Resume")
        pend_v = self._version(pending, 1, "", "ds.docx", "docx",
                               status=ResumeVersion.ParseStatus.PENDING)
        pending.current_version = pend_v
        pending.save(update_fields=["current_version"])

        # 4) Parsing (in progress).
        parsing = Resume.objects.create(user=user, title="Product Manager Resume")
        par_v = self._version(parsing, 1, "", "pm.docx", "docx",
                              status=ResumeVersion.ParseStatus.PARSING)
        parsing.current_version = par_v
        parsing.save(update_fields=["current_version"])

        # 5) Failed parse.
        failed = Resume.objects.create(user=user, title="Corrupted Resume")
        fail_v = self._version(failed, 1, "", "bad.pdf", "pdf", pdf=True,
                               status=ResumeVersion.ParseStatus.FAILED)
        fail_v.parse_error = "Unable to extract text: file is not a valid PDF."
        fail_v.save(update_fields=["parse_error"])
        failed.current_version = fail_v
        failed.save(update_fields=["current_version"])

        self.stdout.write("• Created resumes (parsed/versioned, pdf, pending, parsing, failed)")
        return {"parsed": parsed, "pdf": pdf_resume}

    def _version(self, resume, n, text, name, ftype, *, parsed=False, pdf=False,
                 status=None) -> ResumeVersion:
        file = make_pdf(name) if pdf else make_docx(text or "resume", name)
        v = ResumeVersion.objects.create(
            resume=resume, version=n, file=file, original_filename=name,
            file_type=ftype, size_bytes=len(file),
            parse_status=status or (
                ResumeVersion.ParseStatus.PARSED if parsed else ResumeVersion.ParseStatus.PENDING
            ),
            parsed_json={"raw_text": text, "char_count": len(text)} if parsed else None,
            parse_schema_version="extract.v1" if parsed else "",
        )
        return v

    def _jobs(self, user) -> dict:
        specs = [
            ("Acme", "Senior Backend Engineer", EmploymentType.FULL_TIME,
             ["Python", "Django", "PostgreSQL", "AWS", "Docker"], "Remote", False),
            ("Vercel", "Frontend Engineer", EmploymentType.FULL_TIME,
             ["React", "TypeScript", "Tailwind"], "Remote", False),
            ("OpenAI", "Machine Learning Engineer", EmploymentType.CONTRACT,
             ["Python", "PyTorch", "NLP"], "San Francisco", False),
            ("Startup", "Growth Marketer", EmploymentType.PART_TIME,
             [], "New York", False),
            ("BigCorp", "DevOps Intern", EmploymentType.INTERNSHIP,
             ["Docker", "Kubernetes", "CI/CD"], "Austin", True),  # archived
        ]
        jobs = {}
        for company, title, etype, skills, loc, archived in specs:
            job = JobDescription.objects.create(
                user=user, company_name=company, job_title=title,
                description=f"We are hiring a {title} at {company}. "
                            "This role requires strong fundamentals and collaboration.",
                required_skills=skills, location=loc, employment_type=etype,
            )
            if archived:
                job.is_archived = True
                job.archived_at = timezone.now()
                job.save(update_fields=["is_archived", "archived_at"])
            jobs[title] = job
        self.stdout.write("• Created jobs (full-time, contract, part-time, internship, archived)")
        return jobs

    def _analyses(self, user, resumes, jobs):
        parsed, pdf = resumes["parsed"], resumes["pdf"]
        backend = jobs["Senior Backend Engineer"]
        frontend = jobs["Frontend Engineer"]
        ml = jobs["Machine Learning Engineer"]

        # completed — high match
        self._analysis(
            user, parsed, backend, Analysis.Status.COMPLETED,
            result(88, 92, ["Python", "Django", "PostgreSQL", "AWS"], ["Docker"]),
        )
        # completed — medium match
        self._analysis(
            user, parsed, frontend, Analysis.Status.COMPLETED,
            result(64, 80, ["TypeScript"], ["React", "Tailwind"]),
        )
        # completed — low match
        self._analysis(
            user, pdf, ml, Analysis.Status.COMPLETED,
            result(38, 70, ["Python"], ["PyTorch", "NLP"]),
        )
        # processing
        self._analysis(user, parsed, ml, Analysis.Status.PROCESSING, None)
        # pending
        self._analysis(user, pdf, backend, Analysis.Status.PENDING, None)
        # failed
        a = self._analysis(user, pdf, frontend, Analysis.Status.FAILED, None)
        a.error = "AI provider request failed after 3 retries."
        a.completed_at = timezone.now()
        a.save(update_fields=["error", "completed_at"])

        self.stdout.write("• Created analyses (completed x3, processing, pending, failed)")

    def _analysis(self, user, resume, job, status, res) -> Analysis:
        now = timezone.now()
        job_text = f"{job.job_title}\n{job.description}\n" + ", ".join(job.required_skills)
        a = Analysis.objects.create(
            user=user, resume=resume, resume_version=resume.current_version,
            job_description=job, resume_text=resume.current_version.parsed_json.get("raw_text", ""),
            job_text=job_text, status=status, provider="fake", model="fake-strong",
            prompt_version="analysis.resume.v1",
        )
        if status in (Analysis.Status.PROCESSING, Analysis.Status.PENDING):
            a.started_at = now if status == Analysis.Status.PROCESSING else None
            a.save(update_fields=["started_at"])
        if res is not None:
            a.result_json = res
            a.score = res["score"]
            a.ats_score = res["ats_score"]
            a.result_schema_version = "analysis.resume.v1"
            a.started_at = now
            a.completed_at = now
            a.save()
            AIGenerationLog.objects.create(
                user=user, analysis=a, provider="fake", model="fake-strong",
                prompt_version="analysis.resume.v1", status=AIGenerationLog.Status.SUCCESS,
                tokens_in=850, tokens_out=320, latency_ms=1400,
            )
        elif status == Analysis.Status.FAILED:
            AIGenerationLog.objects.create(
                user=user, analysis=a, provider="fake", model="fake-strong",
                prompt_version="analysis.resume.v1", status=AIGenerationLog.Status.ERROR,
                latency_ms=900, error="provider timeout",
            )
        return a

    def _notifications(self, user):
        analyses = Analysis.objects.filter(user=user).order_by("-created_at")
        completed = analyses.filter(status=Analysis.Status.COMPLETED).first()
        failed = analyses.filter(status=Analysis.Status.FAILED).first()

        Notification.objects.create(
            user=user, type=Notification.Type.SYSTEM,
            title="Welcome to AI Resume Analyzer",
            message="Upload a resume and a job to run your first analysis.",
            is_read=False,
        )
        if completed:
            Notification.objects.create(
                user=user, type=Notification.Type.ANALYSIS_COMPLETE,
                title="Your resume analysis is ready",
                message=f"Match score {completed.score}% (ATS {completed.ats_score}%).",
                data={"analysis_id": str(completed.id), "score": completed.score},
                is_read=False,
            )
        if failed:
            Notification.objects.create(
                user=user, type=Notification.Type.ANALYSIS_FAILED,
                title="An analysis could not be completed",
                message="Please try running it again.",
                data={"analysis_id": str(failed.id)},
                is_read=True,
            )
        self.stdout.write("• Created notifications (system, complete unread, failed read)")
