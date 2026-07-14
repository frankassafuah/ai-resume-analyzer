"""Analysis service — runs a resume-vs-JD analysis and persists the result.

Depends on the AI layer (ai.ResumeAnalyzer) for the provider-agnostic analysis,
and owns the Analysis lifecycle: create -> processing -> completed/failed. The
run itself is synchronous here; M4 wraps this in a Celery task + REST/SSE layer.
"""
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

    def analyze(
        self,
        *,
        user,
        resume_text: str,
        job_text: str,
        resume=None,
        resume_version=None,
        job=None,
    ) -> Analysis:
        if not resume_text.strip() or not job_text.strip():
            raise ValidationError("Both resume text and job description are required.")

        analysis = Analysis.objects.create(
            user=user,
            resume=resume,
            resume_version=resume_version,
            job_description=job,
            resume_text=resume_text,
            job_text=job_text,
            status=Analysis.Status.PROCESSING,
            started_at=timezone.now(),
        )

        try:
            result = self.analyzer.analyze(
                resume_text=resume_text,
                job_description=job_text,
                user=user,
                analysis=analysis,
            )
        except AIError as exc:
            analysis.status = Analysis.Status.FAILED
            analysis.error = str(exc)[:2000]
            analysis.completed_at = timezone.now()
            analysis.save(update_fields=["status", "error", "completed_at", "updated_at"])
            self.logger.error("Analysis %s failed: %s", analysis.id, exc)
            raise

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

    def analyze_resume(self, *, user, resume, job) -> Analysis:
        """Convenience: pull text from a stored Resume + JobDescription."""
        version = resume.current_version
        if version is None or not (version.parsed_json or {}).get("raw_text"):
            raise ValidationError("Resume has no parsed text yet; try again shortly.")
        job_text = f"{job.job_title}\n{job.description}\n" + ", ".join(job.required_skills)
        return self.analyze(
            user=user,
            resume_text=version.parsed_json["raw_text"],
            job_text=job_text,
            resume=resume,
            resume_version=version,
            job=job,
        )
