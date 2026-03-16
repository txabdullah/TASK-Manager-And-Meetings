from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import Team, TeamMember, TeamInvite
from .serializers import (
    TeamSerializer,
    TeamDetailSerializer,
    TeamCreateSerializer,
    TeamMemberSerializer,
    TeamInviteSerializer,
)
from core.permissions import IsTeamMember, IsTeamAdminOrOwner, IsTeamOwner

User = get_user_model()


class TeamListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "POST":
            return TeamCreateSerializer
        return TeamSerializer

    def get_queryset(self):
        return Team.objects.filter(members__user=self.request.user).distinct()

    def perform_create(self, serializer):
        serializer.save()


class TeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TeamDetailSerializer
    permission_classes = [IsTeamMember]

    def get_queryset(self):
        return Team.objects.filter(members__user=self.request.user).distinct()

    def get_permissions(self):
        if self.request.method in ("PATCH", "PUT"):
            return [IsTeamAdminOrOwner()]
        if self.request.method == "DELETE":
            return [IsTeamOwner()]
        return [IsTeamMember()]


class TeamInviteView(APIView):
    permission_classes = [IsTeamAdminOrOwner]

    def post(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        self.check_object_permissions(request, team)
        serializer = TeamInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        role = serializer.validated_data["role"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            TeamInvite.objects.update_or_create(
                team=team,
                email=email,
                defaults={"role": role, "invited_by": request.user},
            )
            return Response(
                {"detail": f"Invitation sent to {email}. They can join once they register."},
                status=status.HTTP_201_CREATED,
            )
        if TeamMember.objects.filter(team=team, user=user).exists():
            return Response(
                {"detail": "User is already a team member."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        TeamMember.objects.create(team=team, user=user, role=role)
        TeamInvite.objects.filter(team=team, email=email).delete()
        return Response(
            {"detail": f"{user.username} has been added to the team."},
            status=status.HTTP_201_CREATED,
        )


class TeamMemberListView(generics.ListAPIView):
    serializer_class = TeamMemberSerializer
    permission_classes = [IsTeamMember]

    def get_queryset(self):
        team = get_object_or_404(Team, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, team)
        return team.members.all()


class TeamMemberRemoveView(APIView):
    permission_classes = [IsTeamAdminOrOwner]

    def delete(self, request, pk, user_id):
        team = get_object_or_404(Team, pk=pk)
        self.check_object_permissions(request, team)
        member = get_object_or_404(TeamMember, team=team, user_id=user_id)
        if member.role == "owner":
            return Response(
                {"detail": "Cannot remove the team owner."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.user == member.user and member.role != "owner":
            member.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
