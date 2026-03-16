from django.urls import path

from .views import (
    MeetingListCreateView,
    MeetingDetailView,
    MeetingNotesCreateView,
    MeetingRecordingCreateView,
)

urlpatterns = [
    path("meetings/", MeetingListCreateView.as_view()),
    path("meetings/<int:pk>/", MeetingDetailView.as_view()),
    path("meetings/<int:pk>/notes/", MeetingNotesCreateView.as_view()),
    path("meetings/<int:pk>/recordings/", MeetingRecordingCreateView.as_view()),
]
