"""Views for user notifications: list, mark one read, mark all read."""
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer


@extend_schema(tags=["notifications"])
class NotificationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    filterset_fields = ["is_read", "type"]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @extend_schema(request=None, responses={200: NotificationSerializer},
                   summary="Mark a notification as read")
    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        note = self.get_object()
        if not note.is_read:
            note.is_read = True
            note.save(update_fields=["is_read", "updated_at"])
        return Response(NotificationSerializer(note).data)

    @extend_schema(request=None, responses={200: None},
                   summary="Mark all notifications as read")
    @action(detail=False, methods=["post"], url_path="read-all")
    def read_all(self, request):
        updated = self.get_queryset().filter(is_read=False).update(
            is_read=True, updated_at=timezone.now()
        )
        return Response({"marked_read": updated})
