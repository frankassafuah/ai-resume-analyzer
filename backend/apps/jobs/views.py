"""Views for job descriptions.

Thin layer: validate via write serializer -> call JobService -> serialize with the
read serializer. Owner-scoped queryset (non-owners get 404). The list is the
user's full history (active + archived); filter/search/paginate to narrow it.
"""
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.jobs.filters import JobDescriptionFilter
from apps.jobs.models import JobDescription
from apps.jobs.serializers import (
    JobDescriptionSerializer,
    JobDescriptionWriteSerializer,
)
from apps.jobs.services import JobService


@extend_schema(tags=["jobs"])
class JobDescriptionViewSet(viewsets.ModelViewSet):
    """CRUD + archive/unarchive for job descriptions, with filtering, search,
    ordering and pagination."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JobDescriptionFilter
    search_fields = ["job_title", "company_name", "description"]
    ordering_fields = ["created_at", "updated_at", "job_title", "company_name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return JobDescription.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return JobDescriptionWriteSerializer
        return JobDescriptionSerializer

    def _service(self) -> JobService:
        return JobService()

    def _read(self, job) -> dict:
        return JobDescriptionSerializer(job, context=self.get_serializer_context()).data

    # --- create / update route through the service ------------------------
    def create(self, request, *args, **kwargs):
        serializer = JobDescriptionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = self._service().create(user=request.user, **serializer.validated_data)
        return Response(self._read(job), status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = JobDescriptionWriteSerializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        job = self._service().update(instance, **serializer.validated_data)
        return Response(self._read(job))

    def perform_destroy(self, instance: JobDescription) -> None:
        self._service().delete(instance)  # soft delete

    # --- archive / unarchive ---------------------------------------------
    @extend_schema(request=None, responses={200: JobDescriptionSerializer},
                   summary="Archive a job description")
    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        job = self._service().archive(self.get_object())
        return Response(self._read(job))

    @extend_schema(request=None, responses={200: JobDescriptionSerializer},
                   summary="Unarchive a job description")
    @action(detail=True, methods=["post"])
    def unarchive(self, request, pk=None):
        job = self._service().unarchive(self.get_object())
        return Response(self._read(job))
