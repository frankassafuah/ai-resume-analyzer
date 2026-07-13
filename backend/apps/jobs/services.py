"""Service layer for job descriptions."""
from typing import Any

from apps.common.services import BaseService
from apps.jobs.models import JobDescription
from apps.jobs.repositories import JobDescriptionRepository


class JobService(BaseService):
    def __init__(self, repo: JobDescriptionRepository | None = None) -> None:
        super().__init__()
        self.repo = repo or JobDescriptionRepository()

    def create(self, *, user, **data: Any) -> JobDescription:
        job = self.repo.create(user=user, **data)
        self.logger.info("Job description %s created", job.id)
        return job

    def update(self, job: JobDescription, **data: Any) -> JobDescription:
        for field, value in data.items():
            setattr(job, field, value)
        job.save(update_fields=[*data.keys(), "updated_at"])
        return job

    def archive(self, job: JobDescription) -> JobDescription:
        job.archive()
        return job

    def unarchive(self, job: JobDescription) -> JobDescription:
        job.unarchive()
        return job

    def delete(self, job: JobDescription) -> None:
        job.delete()  # soft delete
