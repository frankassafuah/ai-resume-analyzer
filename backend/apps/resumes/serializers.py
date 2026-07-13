"""Serializers for resume upload, parsing, and versioning.

Input serializers validate uploads (delegating to the secure file validator);
output serializers shape responses and expose a download URL that points at the
authenticated download endpoint — never the raw storage path.
"""
from rest_framework import serializers
from rest_framework.reverse import reverse

from apps.resumes.models import Resume, ResumeVersion
from apps.resumes.validators import validate_resume_file


# --- output ---------------------------------------------------------------
class ResumeVersionSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = ResumeVersion
        fields = [
            "id",
            "version",
            "original_filename",
            "file_type",
            "size_bytes",
            "parse_status",
            "parse_error",
            "parsed_json",
            "created_at",
            "download_url",
        ]
        read_only_fields = fields

    def get_download_url(self, obj: ResumeVersion) -> str | None:
        request = self.context.get("request")
        if request is None:
            return None
        return reverse(
            "v1:resumes:resume-version-download",
            kwargs={"pk": obj.resume_id, "version_id": obj.id},
            request=request,
        )


class ResumeSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    current_version = ResumeVersionSerializer(read_only=True)
    versions_count = serializers.IntegerField(source="versions.count", read_only=True)

    class Meta:
        model = Resume
        fields = [
            "id",
            "title",
            "status",
            "current_version",
            "versions_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


# --- input ----------------------------------------------------------------
class ResumeUploadSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False, allow_blank=True)
    file = serializers.FileField(write_only=True)

    def validate_file(self, value):
        self.context["file_type"] = validate_resume_file(value)
        return value


class ResumeVersionUploadSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True)

    def validate_file(self, value):
        self.context["file_type"] = validate_resume_file(value)
        return value
