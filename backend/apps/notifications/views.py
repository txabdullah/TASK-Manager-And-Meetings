from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationMarkReadView(APIView):
    def patch(self, request, pk):
        notification = Notification.objects.filter(user=request.user, pk=pk).first()
        if not notification:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        notification.read = True
        notification.save()
        return Response(NotificationSerializer(notification).data)


class NotificationMarkAllReadView(APIView):
    def post(self, request):
        updated = Notification.objects.filter(user=request.user, read=False).update(read=True)
        return Response({"detail": f"Marked {updated} notifications as read."})
