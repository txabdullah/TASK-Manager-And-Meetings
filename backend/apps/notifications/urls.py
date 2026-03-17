from django.urls import path

from .views import (
    NotificationListView,
    NotificationMarkReadView,
    NotificationMarkAllReadView,
)

urlpatterns = [
    path("notifications/", NotificationListView.as_view()),
    path("notifications/<int:pk>/read/", NotificationMarkReadView.as_view()),
    path("notifications/mark-all-read/", NotificationMarkAllReadView.as_view()),
]
