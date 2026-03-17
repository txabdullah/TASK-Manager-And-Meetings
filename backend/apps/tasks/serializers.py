from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Task, TaskAssignment, TaskComment

User = get_user_model()


class TaskAssigneeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="assignee.username", read_only=True)
    email = serializers.EmailField(source="assignee.email", read_only=True)

    class Meta:
        model = TaskAssignment
        fields = ("id", "assignee", "username", "email", "assigned_at")
        read_only_fields = ("id", "assigned_at")


class TaskCommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = TaskComment
        fields = ("id", "author", "author_username", "content", "created_at")
        read_only_fields = ("id", "author", "created_at")


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "meeting",
            "team",
            "title",
            "description",
            "status",
            "deadline",
            "created_by",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "created_by")


class TaskDetailSerializer(TaskSerializer):
    assignments = TaskAssigneeSerializer(many=True, read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)

    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields + ("assignments", "comments")


class TaskAssignSerializer(serializers.Serializer):
    assignee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
    )
