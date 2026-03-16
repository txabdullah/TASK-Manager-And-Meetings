from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Team, TeamMember, TeamInvite

User = get_user_model()


class TeamMemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = TeamMember
        fields = ("id", "user", "username", "email", "first_name", "last_name", "role", "joined_at")
        read_only_fields = ("id", "joined_at")


class TeamSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ("id", "name", "description", "created_by", "created_at", "member_count")
        read_only_fields = ("id", "created_at", "created_by")

    def get_member_count(self, obj):
        return obj.members.count()


class TeamDetailSerializer(TeamSerializer):
    members = TeamMemberSerializer(many=True, read_only=True)

    class Meta(TeamSerializer.Meta):
        fields = TeamSerializer.Meta.fields + ("members",)


class TeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("id", "name", "description")
        read_only_fields = ("id",)

    def create(self, validated_data):
        request = self.context.get("request")
        team = Team.objects.create(created_by=request.user, **validated_data)
        TeamMember.objects.create(team=team, user=request.user, role="owner")
        return team


class TeamInviteSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=TeamMember.ROLE_CHOICES, default="member")
