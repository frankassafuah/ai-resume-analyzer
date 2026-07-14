"""Analysis service — runs a resume-vs-JD analysis and persists the result.

Two entry points:
- `analyze(...)` / `analyze_resume(...)` — synchronous (used in tests/shell).
- `request_analysis(...)` + `run(analysis_id)` — the async path: create a pending
  row, enqueue the Celery pipeline, and let `run_analysis` execute + notify.

The AI work is delegated to ai.ResumeAnalyzer (provider-agnostic). This service
owns only the Analysis lifecycle: pending -> processing -> completed/failed.
"""
from django.db import transaction
from django.utils import timezone

from apps.ai.exceptions import AIError
from apps.ai.services import ResumeAnalyzer
from apps.analysis.models import Analysis
from apps.common.exceptions import ValidationError
from apps.common.services import BaseService


class AnalysisService(BaseService):
    def __init__(self, analyzer: ResumeAnalyzer | None = None) -> None:
        super().__init__()
        self.analyzer = analyzer or ResumeAnalyzer()

    # --- creation ---------------------------------------------------------
    def _create(
        self, *, user, resume_text, job_text, resume=None, resume_version=None,
        job=None, status=Analysis.Status.PENDING,
    ) -> Analysis:
        return Analysis.objects.create(
            user=user,
            resume=resume,
            resume_version=resume_version,
            job_description=job,
            resume_text=resume_text,
            job_text=job_text,
            status=status,
        )

    @staticmethod
    def _job_text(job) -> str:
        return f"{job.job_title}\n{job.description}\n" + ", ".join(job.required_skills)

    # --- synchronous path (tests / direct use) ----------------------------
    def analyze(
        self, *, user, resume_text, job_text, resume=None, resume_version=None, job=None
    ) -> Analysis:
        if not resume_text.strip() or not job_text.strip():
            raise ValidationError("Both resume text and job description are required.")
        analysis = self._create(
            user=user, resume_text=resume_text, job_text=job_text,
            resume=resume, resume_version=resume_version, job=job,
            status=Analysis.Status.PROCESSING,
        )
        analysis.started_at = timezone.now()
        analysis.save(update_fields=["started_at", "status", "updated_at"])
        try:
            return self._execute(analysis)
        except AIError as exc:
            self.mark_failed(analysis, str(exc))
            raise

    def analyze_resume(self, *, user, resume, job) -> Analysis:
        text = self._resume_text(resume)
        return self.analyze(
            user=user, resume_text=text, job_text=self._job_text(job),
            resume=resume, resume_version=resume.current_version, job=job,
        )

    # --- async path -------------------------------------------------------
    def request_analysis(self, *, user, resume, job) -> Analysis:
        """Create a pending analysis and enqueue the Celery pipeline. If the
        resume isn't parsed yet, the pipeline parses first, then analyzes."""
        version = resume.current_version
        if version is None:
            raise ValidationError("Resume has no uploaded file to analyze.")

        parsed_text = (version.parsed_json or {}).get("raw_text", "")
        analysis = self._create(
            user=user, resume_text=parsed_text, job_text=self._job_text(job),
            resume=resume, resume_version=version, job=job,
            status=Analysis.Status.PENDING,
        )
        self._enqueue_pipeline(analysis, version)
        return analysis

    def run(self, analysis_id) -> Analysis:
        """Task body: execute a pending/processing analysis. Raises on AI failure
        so the task can retry; does NOT mark failed (the task decides)."""
        analysis = Analysis.objects.select_related("resume_version").get(pk=analysis_id)

        if not analysis.resume_text and analysis.resume_version_id:
            text = (analysis.resume_version.parsed_json or {}).get("raw_text", "")
            if not text:
                raise ValidationError("Resume is not parsed yet.")
            analysis.resume_text = text

        analysis.status = Analysis.Status.PROCESSING
        analysis.started_at = analysis.started_at or timezone.now()
        analysis.save(update_fields=["status", "started_at", "resume_text", "updated_at"])
        return self._execute(analysis)

    def mark_failed(self, analysis, error: str) -> Analysis:
        if isinstance(analysis, str):
            analysis = Analysis.objects.get(pk=analysis)
        analysis.status = Analysis.Status.FAILED
        analysis.error = str(error)[:2000]
        analysis.completed_at = timezone.now()
        analysis.save(update_fields=["status", "error", "completed_at", "updated_at"])
        self.logger.error("Analysis %s failed: %s", analysis.id, error)
        return analysis

    # --- core -------------------------------------------------------------
    def _execute(self, analysis: Analysis) -> Analysis:
        result = self.analyzer.analyze(
            resume_text=analysis.resume_text,
            job_description=analysis.job_text,
            user=analysis.user,
            analysis=analysis,
        )
        analysis.result_json = result.model_dump()
        analysis.score = result.score
        analysis.ats_score = result.ats_score
        analysis.result_schema_version = self.analyzer.prompt_version
        analysis.prompt_version = self.analyzer.prompt_version
        analysis.provider = self.analyzer.gateway.provider.name
        analysis.status = Analysis.Status.COMPLETED
        analysis.completed_at = timezone.now()
        analysis.save()
        self.logger.info("Analysis %s completed (score=%s)", analysis.id, result.score)
        return analysis

    def _resume_text(self, resume) -> str:
        version = resume.current_version
        if version is None or not (version.parsed_json or {}).get("raw_text"):
            raise ValidationError("Resume has no parsed text yet; try again shortly.")
        return version.parsed_json["raw_text"]

    @staticmethod
    def _enqueue_pipeline(analysis: Analysis, version) -> None:
        from celery import chain

        from apps.analysis.tasks import run_analysis
        from apps.resumes.tasks import parse_resume_version

        aid = str(analysis.id)
        parsed = version.parsed_json and version.parsed_json.get("raw_text")
        if parsed:
            sig = run_analysis.si(aid)
        else:
            # Parse first, then analyze — guarantees text is ready (the flow:
            # upload -> extract -> analyze -> save -> notify).
            sig = chain(parse_resume_version.si(str(version.id)), run_analysis.si(aid))
        # Enqueue only after the pending row is committed, so the worker sees it.
        transaction.on_commit(sig.delay)
