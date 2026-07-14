"""Views for analysis runs.

POST creates a pending analysis and kicks off the async pipeline (202); GET lists
history or polls a single run's status/result. Ownership is enforced by scoping
querysets to the requesting user.
"""
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.analysis.models import Analysis
from apps.analysis.serializers import AnalysisCreateSerializer, AnalysisSerializer
from apps.analysis.services import AnalysisService
from apps.jobs.models import JobDescription
from apps.resumes.models import Resume


@extend_schema(tags=["analysis"])
class AnalysisViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]
    serializer_class = AnalysisSerializer

    def get_queryset(self):
        return Analysis.objects.filter(user=self.request.user).order_by("-created_at")

    @extend_schema(
        request=AnalysisCreateSerializer,
        responses={202: AnalysisSerializer},
        summary="Start an analysis of a resume against a job description (async)",
    )
    def create(self, request, *args, **kwargs):
        serializer = AnalysisCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Resolve owned resume + job (404 via get_object_or_404-style scoping).
        resume = self._get_owned(Resume, serializer.validated_data["resume_id"])
        job = self._get_owned(JobDescription, serializer.validated_data["job_id"])

        analysis = AnalysisService().request_analysis(
            user=request.user, resume=resume, job=job
        )
        return Response(
            AnalysisSerializer(analysis).data, status=status.HTTP_202_ACCEPTED
        )

    def _get_owned(self, model, pk):
        from rest_framework.exceptions import NotFound

        obj = model.objects.filter(user=self.request.user, pk=pk).first()
        if obj is None:
            raise NotFound(f"{model.__name__} not found.")
        return obj
