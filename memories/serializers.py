from rest_framework import serializers
from django.db import models
from .models import UserMemory, TeamMemory, OrganizationMemory
from user.models import User, Team, Organization


class UserMemorySerializer(serializers.ModelSerializer):
    """
    Serializer for user-scoped memories.
    """

    class Meta:
        model = UserMemory
        fields = [
            "id",
            "content",
            "mem0_memory_id",
            "status",
            "error_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "mem0_memory_id",
            "status",
            "error_message",
        ]

    def create(self, validated_data):
        """Set user to current user."""
        validated_data["user"] = self.context["request"].user
        return UserMemory.objects.create(**validated_data)


class TeamMemorySerializer(serializers.ModelSerializer):
    """
    Serializer for team-scoped memories.
    """

    class Meta:
        model = TeamMemory
        fields = [
            "id",
            "team",
            "content",
            "mem0_memory_id",
            "status",
            "error_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "team",
            "created_at",
            "updated_at",
            "mem0_memory_id",
            "status",
            "error_message",
        ]

    def create(self, validated_data):
        """Create team memory."""
        return TeamMemory.objects.create(**validated_data)


class OrganizationMemorySerializer(serializers.ModelSerializer):
    """
    Serializer for organization-scoped memories.
    """

    class Meta:
        model = OrganizationMemory
        fields = [
            "id",
            "organization",
            "content",
            "mem0_memory_id",
            "status",
            "error_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "organization",
            "created_at",
            "updated_at",
            "mem0_memory_id",
            "status",
            "error_message",
        ]

    def create(self, validated_data):
        """Create organization memory."""
        return OrganizationMemory.objects.create(**validated_data)
