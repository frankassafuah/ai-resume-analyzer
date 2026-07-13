"""Service layer for resume upload, parsing, and versioning.

Owns the transactional workflow: create a resume with its first version, append
new versions, point `current_version`, and hand parsing off to Celery. Views call
these; they never build querysets or touch Celery directly.
"""
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from apps.common.services import BaseService
from apps.resumes.models import Resume, ResumeVersion
from apps.resumes.repositories import ResumeRepository, ResumeVersionRepository


class ResumeService(BaseService):
    def __init__(
        self,
        resumes: ResumeRepository | None = None,
        versions: ResumeVersionRepository | None = None,
    ) -> None:
        super().__init__()
        self.resumes = resumes or ResumeRepository()
        self.versions = versions or ResumeVersionRepository()

    @transaction.atomic
    def create_resume(
        self, *, user, uploaded_file: UploadedFile, file_type: str, title: str = ""
    ) -> Resume:
        resume = self.resumes.create(
            user=user, title=title or self._default_title(uploaded_file)
        )
        self._add_version(resume, uploaded_file, file_type, version=1)
        return resume

    @transaction.atomic
    def add_version(
        self, *, resume: Resume, uploaded_file: UploadedFile, file_type: str
    ) -> ResumeVersion:
        number = self.versions.next_version_number(resume)
        return self._add_version(resume, uploaded_file, file_type, version=number)

    def _add_version(
        self, resume: Resume, uploaded_file: UploadedFile, file_type: str, version: int
    ) -> ResumeVersion:
        version_obj = self.versions.create(
            resume=resume,
            version=version,
            file=uploaded_file,
            original_filename=uploaded_file.name or f"resume.{file_type}",
            file_type=file_type,
            size_bytes=uploaded_file.size or 0,
        )
        resume.current_version = version_obj
        resume.save(update_fields=["current_version", "updated_at"])
        self._enqueue_parse(version_obj.id)
        self.logger.info(
            "Resume %s version %s uploaded", resume.id, version_obj.version
        )
        return version_obj

    def delete_resume(self, resume: Resume) -> None:
        resume.delete()  # soft delete

    @staticmethod
    def _default_title(uploaded_file: UploadedFile) -> str:
        name = uploaded_file.name or "Resume"
        return name.rsplit(".", 1)[0][:255]

    @staticmethod
    def _enqueue_parse(version_id) -> None:
        # Imported lazily to avoid a circular import (tasks import models/services).
        from apps.resumes.tasks import parse_resume_version

        # Run after the surrounding DB transaction commits so the worker can see
        # the freshly created row.
        transaction.on_commit(lambda: parse_resume_version.delay(str(version_id)))
