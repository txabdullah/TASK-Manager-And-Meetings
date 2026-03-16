from rest_framework import serializers

from .models import Meeting, MeetingNotes, MeetingRecording


class MeetingNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingNotes
        fields = ("id", "content", "uploaded_at")
        read_only_fields = ("id", "uploaded_at")


class MeetingRecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingRecording
        fields = ("id", "file", "url", "uploaded_at")
        read_only_fields = ("id", "uploaded_at")


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ("id", "team", "title", "date", "created_by", "created_at")
        read_only_fields = ("id", "created_at", "created_by")


class MeetingDetailSerializer(MeetingSerializer):
    notes = MeetingNotesSerializer(many=True, read_only=True)
    recordings = MeetingRecordingSerializer(many=True, read_only=True)

    class Meta(MeetingSerializer.Meta):
        fields = MeetingSerializer.Meta.fields + ("notes", "recordings")


class MeetingNotesCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingNotes
        fields = ("content",)
