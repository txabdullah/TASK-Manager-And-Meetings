from rest_framework import permissions


class IsTeamMember(permissions.BasePermission):
    """User must be a member of the team."""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "team"):
            team = obj.team
        else:
            team = obj
        return team.members.filter(user=request.user).exists()


class IsTeamAdminOrOwner(permissions.BasePermission):
    """User must be admin or owner of the team."""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "team"):
            team = obj.team
        else:
            team = obj
        membership = team.members.filter(user=request.user).first()
        if not membership:
            return False
        return membership.role in ("owner", "admin")


class IsTeamOwner(permissions.BasePermission):
    """User must be owner of the team."""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "team"):
            team = obj.team
        else:
            team = obj
        membership = team.members.filter(user=request.user).first()
        if not membership:
            return False
        return membership.role == "owner"
