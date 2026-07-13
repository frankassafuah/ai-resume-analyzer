"""Views for resume upload, parsing, and versioning.

Thin layer: validate via serializer -> call ResumeService -> serialize. Ownership
is enforced by scoping the queryset to the requesting user, so non-owners get 404.
File downloads stream through an authenticated, owner-checked endpoint (never the
raw storage path) and bypass the JSON envelope.
"""
from django.http import FileResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.resumes.models import Resume
from apps.resumes.serializers import (
    ResumeSerializer,
    ResumeUploadSerializer,
    ResumeVersionSerializer,
    ResumeVersionUploadSerializer,
)
from apps.resumes.services import ResumeService

_CONTENT_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@extend_schema(tags=["resumes"])
class ResumeViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """List, upload, view, delete resumes; manage versions; download files."""

    permission_classes = [IsAuthenticated]
    serializer_class = ResumeSerializer

    def get_queryset(self):
        # Owner-scoped; SoftDeleteModel manager already hides deleted resumes.
        return (
            Resume.objects.filter(user=self.request.user)
            .select_related("current_version")
            .prefetch_related("versions")
        )

    # --- upload (create) --------------------------------------------------
    @extend_schema(
        request=ResumeUploadSerializer,
        responses={201: ResumeSerializer},
        summary="Upload a resume (PDF/DOCX) — creates version 1",
    )
    def create(self, request, *args, **kwargs):
        serializer = ResumeUploadSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        resume = ResumeService().create_resume(
            user=request.user,
            uploaded_file=serializer.validated_data["file"],
            file_type=serializer.context["file_type"],
            title=serializer.validated_data.get("title", ""),
        )
        out = ResumeSerializer(resume, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    # --- delete (soft) ----------------------------------------------------
    def perform_destroy(self, instance: Resume) -> None:
        ResumeService().delete_resume(instance)

    # --- versions ---------------------------------------------------------
    @extend_schema(
        methods=["GET"],
        responses={200: ResumeVersionSerializer(many=True)},
        summary="List a resume's versions",
    )
    @extend_schema(
        methods=["POST"],
        request=ResumeVersionUploadSerializer,
        responses={201: ResumeVersionSerializer},
        summary="Upload a new version of a resume",
    )
    @action(detail=True, methods=["get", "post"])
    def versions(self, request, pk=None):
        resume = self.get_object()
        if request.method == "POST":
            serializer = ResumeVersionUploadSerializer(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            version = ResumeService().add_version(
                resume=resume,
                uploaded_file=serializer.validated_data["file"],
                file_type=serializer.context["file_type"],
            )
            out = ResumeVersionSerializer(version, context={"request": request})
            return Response(out.data, status=status.HTTP_201_CREATED)

        qs = resume.versions.all()
        out = ResumeVersionSerializer(qs, many=True, context={"request": request})
        return Response(out.data)

    # --- downloads --------------------------------------------------------
    @extend_schema(
        responses={
            (200, "application/octet-stream"): OpenApiTypes.BINARY,
            404: OpenApiResponse(description="No file"),
        },
        summary="Download the current version's file",
    )
    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        resume = self.get_object()
        if not resume.current_version_id:
            raise NotFound("This resume has no uploaded file.")
        return self._stream(resume.current_version)

    @extend_schema(
        responses={(200, "application/octet-stream"): OpenApiTypes.BINARY},
        summary="Download a specific version's file",
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="versions/(?P<version_id>[^/.]+)/download",
    )
    def version_download(self, request, pk=None, version_id=None):
        resume = self.get_object()
        version = resume.versions.filter(id=version_id).first()
        if version is None:
            raise NotFound("Version not found.")
        return self._stream(version)

    @staticmethod
    def _stream(version) -> FileResponse:
        return FileResponse(
            version.file.open("rb"),
            as_attachment=True,
            filename=version.original_filename,
            content_type=_CONTENT_TYPES.get(
                version.file_type, "application/octet-stream"
            ),
        )
