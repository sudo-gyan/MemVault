from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Organization, Team, TeamMembership

User = get_user_model()


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for team member information."""

    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = TeamMembership
        fields = ["user_id", "username", "email", "joined_at"]


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for team CRUD operations."""

    members = TeamMemberSerializer(
        source="teammembership_set", many=True, read_only=True
    )
    member_count = serializers.SerializerMethodField()
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )

    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "description",
            "organization",
            "organization_name",
            "members",
            "member_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organization", "created_at", "updated_at"]

    def get_member_count(self, obj):
        """Get the number of members in the team."""
        return obj.members.count()


class TeamMembershipCreateSerializer(serializers.Serializer):
    """Serializer for adding members to a team."""

    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        """Validate that the user exists."""
        try:
            user = User.objects.get(id=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this ID does not exist.")

    def validate(self, attrs):
        """Additional validation for team membership."""
        team = self.context.get("team")
        user = attrs["user_id"]

        if not team:
            raise serializers.ValidationError("Team context is required.")

        # Check if user is already a member
        if TeamMembership.objects.filter(team=team, user=user).exists():
            raise serializers.ValidationError("User is already a member of this team.")

        return attrs


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for organization information."""

    admin_username = serializers.CharField(source="admin.username", read_only=True)
    team_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "admin",
            "admin_username",
            "team_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "admin", "created_at", "updated_at"]

    def get_team_count(self, obj):
        """Get the number of teams in the organization."""
        return obj.teams.count()
