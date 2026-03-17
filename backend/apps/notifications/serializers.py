from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "notification_type", "read", "created_at", "object_id")
        read_only_fields = ("id", "created_at")
