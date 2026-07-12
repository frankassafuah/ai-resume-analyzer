"""Serializer conventions.

Keep input and output serializers separate:
- `*InputSerializer` / `*CreateSerializer` — validate request bodies. They do NOT
  need to map 1:1 to a model and should not expose server-controlled fields.
- `*OutputSerializer` — shape responses. Read-only.

This avoids the trap of one ModelSerializer serving both directions and leaking
or accepting fields it shouldn't. `TimeStampedOutputSerializer` is a small mixin
for the common id/created_at/updated_at trio.
"""
from rest_framework import serializers


class TimeStampedOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
