"""Repositories for resume upload, parsing, and versioning."""
from django.db.models import Max, QuerySet

from apps.common.repositories import BaseRepository
from apps.resumes.models import Resume, ResumeVersion


class ResumeRepository(BaseRepository[Resume]):
    model = Resume

    def for_user(self, user) -> QuerySet[Resume]:
        return self.get_queryset().filter(user=user).select_related("current_version")


class ResumeVersionRepository(BaseRepository[ResumeVersion]):
    model = ResumeVersion

    def next_version_number(self, resume: Resume) -> int:
        current = (
            self.get_queryset()
            .filter(resume=resume)
            .aggregate(m=Max("version"))["m"]
        )
        return (current or 0) + 1
