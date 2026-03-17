from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Task, TaskAssignment, TaskComment
from .serializers import (
    TaskSerializer,
    TaskDetailSerializer,
    TaskAssigneeSerializer,
    TaskCommentSerializer,
    TaskAssignSerializer,
)
from core.permissions import IsTeamMember


class TaskListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "GET":
            return TaskDetailSerializer
        return TaskSerializer

    def get_queryset(self):
        qs = Task.objects.filter(
            team__members__user=self.request.user
        ).distinct().select_related("team", "meeting", "created_by").prefetch_related("assignments", "assignments__assignee", "comments", "comments__author")
        team = self.request.query_params.get("team")
        assignee = self.request.query_params.get("assignee")
        status_filter = self.request.query_params.get("status")
        if team:
            qs = qs.filter(team_id=team)
        if assignee:
            qs = qs.filter(assignments__assignee_id=assignee)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskDetailSerializer
    permission_classes = [IsTeamMember]

    def get_queryset(self):
        return Task.objects.filter(
            team__members__user=self.request.user
        ).distinct().select_related("team", "meeting", "created_by").prefetch_related("assignments", "assignments__assignee", "comments", "comments__author")


class TaskAssignView(APIView):
    permission_classes = [IsTeamMember]

    def post(self, request, pk):
        task = get_object_or_404(
            Task.objects.filter(team__members__user=request.user),
            pk=pk,
        )
        self.check_object_permissions(request, task)
        serializer = TaskAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team_member_ids = set(
            task.team.members.values_list("user_id", flat=True)
        )
        for user_id in serializer.validated_data["assignee_ids"]:
            if user_id not in team_member_ids:
                return Response(
                    {"detail": f"User {user_id} is not a team member."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            assignment, created = TaskAssignment.objects.get_or_create(
                task=task,
                assignee_id=user_id,
            )
            if created:
                try:
                    from apps.notifications.services import create_task_assigned_notification
                    create_task_assigned_notification(assignment.assignee, task)
                except Exception:
                    pass
        return Response(
            TaskAssigneeSerializer(task.assignments.all(), many=True).data,
            status=status.HTTP_200_OK,
        )


class TaskCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskCommentSerializer
    permission_classes = [IsTeamMember]

    def get_queryset(self):
        task = get_object_or_404(
            Task.objects.filter(team__members__user=self.request.user),
            pk=self.kwargs["pk"],
        )
        self.check_object_permissions(self.request, task)
        return task.comments.select_related("author")

    def perform_create(self, serializer):
        task = get_object_or_404(
            Task.objects.filter(team__members__user=self.request.user),
            pk=self.kwargs["pk"],
        )
        self.check_object_permissions(self.request, task)
        comment = serializer.save(task=task, author=self.request.user)
        try:
            from apps.notifications.services import create_new_comment_notification
            create_new_comment_notification(comment, task)
        except Exception:
            pass
