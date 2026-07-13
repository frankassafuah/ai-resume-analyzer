"""Repositories for job descriptions."""
from django.db.models import QuerySet

from apps.common.repositories import BaseRepository
from apps.jobs.models import JobDescription


class JobDescriptionRepository(BaseRepository[JobDescription]):
    model = JobDescription

    def for_user(self, user) -> QuerySet[JobDescription]:
        return self.get_queryset().filter(user=user)
