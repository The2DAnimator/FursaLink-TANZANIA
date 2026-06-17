from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.notifications.models import Notification, NotificationPreference
from apps.notifications.serializers import (
    NotificationPreferenceSerializer,
    NotificationSerializer,
)


class NotificationViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ("category", "is_read", "channel")

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save(update_fields=["is_read"])
        return Response({"status": "ok"})

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"status": "ok"})

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread": count})

    @action(detail=False, methods=["get", "put", "patch"])
    def preferences(self, request):
        prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
        if request.method == "GET":
            return Response(NotificationPreferenceSerializer(prefs).data)
        serializer = NotificationPreferenceSerializer(prefs, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
