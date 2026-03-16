from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Meeting, MeetingNotes, MeetingRecording
from .serializers import (
    MeetingSerializer,
    MeetingDetailSerializer,
    MeetingNotesSerializer,
    MeetingNotesCreateSerializer,
    MeetingRecordingSerializer,
)
from core.permissions import IsTeamMember


class MeetingListCreateView(generics.ListCreateAPIView):
    serializer_class = MeetingSerializer

    def get_queryset(self):
        return Meeting.objects.filter(
            team__members__user=self.request.user
        ).distinct().select_related("team", "created_by")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return MeetingDetailSerializer
        return MeetingSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class MeetingDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = MeetingDetailSerializer
    permission_classes = [IsTeamMember]

    def get_queryset(self):
        return Meeting.objects.filter(
            team__members__user=self.request.user
        ).distinct().select_related("team", "created_by").prefetch_related("notes", "recordings")


class MeetingNotesCreateView(APIView):
    permission_classes = [IsTeamMember]

    def post(self, request, pk):
        meeting = get_object_or_404(
            Meeting.objects.filter(team__members__user=request.user),
            pk=pk,
        )
        self.check_object_permissions(request, meeting)
        serializer = MeetingNotesCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notes = MeetingNotes.objects.create(
            meeting=meeting,
            content=serializer.validated_data["content"],
        )
        from .tasks import process_meeting_notes
        process_meeting_notes.delay(notes.id)
        return Response(
            MeetingNotesSerializer(notes).data,
            status=status.HTTP_201_CREATED,
        )


class MeetingRecordingCreateView(APIView):
    permission_classes = [IsTeamMember]

    def post(self, request, pk):
        meeting = get_object_or_404(
            Meeting.objects.filter(team__members__user=request.user),
            pk=pk,
        )
        self.check_object_permissions(request, meeting)
        serializer = MeetingRecordingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recording = MeetingRecording.objects.create(
            meeting=meeting,
            **serializer.validated_data,
        )
        return Response(
            MeetingRecordingSerializer(recording).data,
            status=status.HTTP_201_CREATED,
        )
