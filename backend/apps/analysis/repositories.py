"""Repositories for analysis runs."""
from django.db.models import QuerySet

from apps.analysis.models import Analysis
from apps.common.repositories import BaseRepository


class AnalysisRepository(BaseRepository[Analysis]):
    model = Analysis

    def for_user(self, user) -> QuerySet[Analysis]:
        return self.get_queryset().filter(user=user)
