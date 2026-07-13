"""Celery tasks for resume parsing.

`parse_resume_version` runs on the `parsing` queue (routed in settings). It
extracts raw text now; the AI-structured parse will be layered on in M3/M4 by
extending this task to call the LLM gateway. It is idempotent and never raises
into the caller — failures are recorded on the row as `FAILED`.
"""
import logging

from celery import shared_task

from apps.resumes.models import ResumeVersion
from apps.resumes.parsing import PARSE_SCHEMA_VERSION, extract_text

logger = logging.getLogger("apps.resumes")


@shared_task(name="apps.resumes.tasks.parse_resume_version", bind=True, max_retries=2)
def parse_resume_version(self, version_id: str) -> str:
    try:
        version = ResumeVersion.objects.get(pk=version_id)
    except ResumeVersion.DoesNotExist:
        logger.warning("parse_resume_version: version %s not found", version_id)
        return "not_found"

    version.parse_status = ResumeVersion.ParseStatus.PARSING
    version.save(update_fields=["parse_status", "updated_at"])

    try:
        with version.file.open("rb") as fh:
            text = extract_text(fh, version.file_type)
        version.parsed_json = {
            "raw_text": text,
            "char_count": len(text),
            "extractor": version.file_type,
        }
        version.parse_schema_version = PARSE_SCHEMA_VERSION
        version.parse_status = ResumeVersion.ParseStatus.PARSED
        version.parse_error = ""
        version.save(
            update_fields=[
                "parsed_json",
                "parse_schema_version",
                "parse_status",
                "parse_error",
                "updated_at",
            ]
        )
        logger.info("Parsed resume version %s (%d chars)", version_id, len(text))
        return "parsed"
    except Exception as exc:  # noqa: BLE001 — record failure, don't crash the worker
        logger.exception("Failed to parse resume version %s", version_id)
        version.parse_status = ResumeVersion.ParseStatus.FAILED
        version.parse_error = str(exc)[:1000]
        version.save(update_fields=["parse_status", "parse_error", "updated_at"])
        return "failed"
