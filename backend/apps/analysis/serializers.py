"""Serializers for analysis runs.

Input takes references to an owned resume + job; output exposes status and the
stored result. The result body is only meaningful once status == completed.
"""
from rest_framework import serializers

from apps.analysis.models import Analysis


class AnalysisSerializer(serializers.ModelSerializer):
    resume = serializers.UUIDField(source="resume_id", read_only=True)
    job = serializers.UUIDField(source="job_description_id", read_only=True)

    class Meta:
        model = Analysis
        fields = [
            "id",
            "status",
            "score",
            "ats_score",
            "provider",
            "model",
            "result_json",
            "error",
            "resume",
            "job",
            "created_at",
            "started_at",
            "completed_at",
        ]
        read_only_fields = fields


class AnalysisCreateSerializer(serializers.Serializer):
    resume_id = serializers.UUIDField()
    job_id = serializers.UUIDField()
