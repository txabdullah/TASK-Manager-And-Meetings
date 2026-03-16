from django.urls import path

from .views import (
    TeamListCreateView,
    TeamDetailView,
    TeamInviteView,
    TeamMemberListView,
    TeamMemberRemoveView,
)

urlpatterns = [
    path("teams/", TeamListCreateView.as_view()),
    path("teams/<int:pk>/", TeamDetailView.as_view()),
    path("teams/<int:pk>/invite/", TeamInviteView.as_view()),
    path("teams/<int:pk>/members/", TeamMemberListView.as_view()),
    path("teams/<int:pk>/members/<int:user_id>/", TeamMemberRemoveView.as_view()),
]
