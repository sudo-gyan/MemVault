from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import UserMemory, TeamMemory, OrganizationMemory
from .serializers import (
    UserMemorySerializer,
    TeamMemorySerializer,
    OrganizationMemorySerializer,
)
from .permissions import (
    UserMemoryPermission,
    TeamMemoryPermission,
    OrganizationMemoryPermission,
)
from user.models import User, Team, Organization, TeamMembership


class BaseMemoryViewSet:
    """Base mixin for memory views with common functionality."""

    def get_queryset(self):
        """Override in subclasses to provide proper filtering."""
        raise NotImplementedError

    def apply_filters(self, queryset):
        """Apply common filters to queryset."""
        # Filter by status
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Search in content
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(content__icontains=search)

        return queryset


# User Memory Views
class UserMemoryListCreateView(BaseMemoryViewSet, generics.ListCreateAPIView):
    """
    List and create memories for the authenticated user.
    GET /memories/users/me
    POST /memories/users/me
    """

    serializer_class = UserMemorySerializer
    permission_classes = [IsAuthenticated, UserMemoryPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Return only current user's memories."""
        queryset = UserMemory.objects.filter(user=self.request.user)
        return self.apply_filters(queryset)


class UserMemoryDetailView(BaseMemoryViewSet, generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a specific user memory.
    GET/PATCH/DELETE /memories/users/me/<id>
    """

    serializer_class = UserMemorySerializer
    permission_classes = [IsAuthenticated, UserMemoryPermission]
    lookup_url_kwarg = "memory_id"

    def get_queryset(self):
        """Return only current user's memories."""
        return UserMemory.objects.filter(user=self.request.user)


# Team Memory Views
class TeamMemoryListCreateView(BaseMemoryViewSet, generics.ListCreateAPIView):
    """
    List and create memories for a specific team.
    GET /memories/teams/<team_id>
    POST /memories/teams/<team_id>
    """

    serializer_class = TeamMemorySerializer
    permission_classes = [IsAuthenticated, TeamMemoryPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Return memories for the specified team if user has access."""
        team_id = self.kwargs.get("team_id")
        team = get_object_or_404(Team, id=team_id)

        # Check if user has access to this team
        user = self.request.user
        has_access = (
            TeamMembership.objects.filter(user=user, team=team).exists()
            or team.organization.admin == user
        )

        if not has_access:
            return TeamMemory.objects.none()

        queryset = TeamMemory.objects.filter(team=team)
        return self.apply_filters(queryset)

    def perform_create(self, serializer):
        """Set the team for the new memory."""
        team_id = self.kwargs.get("team_id")
        team = get_object_or_404(Team, id=team_id)
        serializer.save(team=team)


class TeamMemoryDetailView(BaseMemoryViewSet, generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a specific team memory.
    GET/PATCH/DELETE /memories/teams/<team_id>/<memory_id>
    """

    serializer_class = TeamMemorySerializer
    permission_classes = [IsAuthenticated, TeamMemoryPermission]
    lookup_url_kwarg = "memory_id"

    def get_queryset(self):
        """Return memories for the specified team if user has access."""
        team_id = self.kwargs.get("team_id")
        team = get_object_or_404(Team, id=team_id)

        # Check if user has access to this team
        user = self.request.user
        has_access = (
            TeamMembership.objects.filter(user=user, team=team).exists()
            or team.organization.admin == user
        )

        if not has_access:
            return TeamMemory.objects.none()

        return TeamMemory.objects.filter(team=team)


# Organization Memory Views
class OrganizationMemoryListCreateView(BaseMemoryViewSet, generics.ListCreateAPIView):
    """
    List and create memories for a specific organization.
    GET /memories/orgs/<org_id>
    POST /memories/orgs/<org_id>
    """

    serializer_class = OrganizationMemorySerializer
    permission_classes = [IsAuthenticated, OrganizationMemoryPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Return memories for the specified organization if user has access."""
        org_id = self.kwargs.get("org_id")
        organization = get_object_or_404(Organization, id=org_id)

        # Check if user has access to this organization
        user = self.request.user
        has_access = (
            organization.admin == user
            or TeamMembership.objects.filter(
                user=user, team__organization=organization
            ).exists()
        )

        if not has_access:
            return OrganizationMemory.objects.none()

        queryset = OrganizationMemory.objects.filter(organization=organization)
        return self.apply_filters(queryset)

    def perform_create(self, serializer):
        """Set the organization for the new memory."""
        org_id = self.kwargs.get("org_id")
        organization = get_object_or_404(Organization, id=org_id)
        serializer.save(organization=organization)


class OrganizationMemoryDetailView(
    BaseMemoryViewSet, generics.RetrieveUpdateDestroyAPIView
):
    """
    Retrieve, update or delete a specific organization memory.
    GET/PATCH/DELETE /memories/orgs/<org_id>/<memory_id>
    """

    serializer_class = OrganizationMemorySerializer
    permission_classes = [IsAuthenticated, OrganizationMemoryPermission]
    lookup_url_kwarg = "memory_id"

    def get_queryset(self):
        """Return memories for the specified organization if user has access."""
        org_id = self.kwargs.get("org_id")
        organization = get_object_or_404(Organization, id=org_id)

        # Check if user has access to this organization
        user = self.request.user
        has_access = (
            organization.admin == user
            or TeamMembership.objects.filter(
                user=user, team__organization=organization
            ).exists()
        )

        if not has_access:
            return OrganizationMemory.objects.none()

        return OrganizationMemory.objects.filter(organization=organization)
