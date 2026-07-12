"""Account serializers. Split input/output per common conventions.
Request-body serializers (register/login) arrive in M1."""
from rest_framework import serializers


class UserOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(read_only=True)
    name = serializers.CharField(read_only=True)
    email_verified = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
