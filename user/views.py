from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db import transaction

from authentication.authentication import APIKeyAuthentication
from .models import Organization, Team, TeamMembership
from .serializers import (
    TeamSerializer, 
    TeamMembershipCreateSerializer, 
    TeamMemberSerializer,
    OrganizationSerializer
)
from .permissions import IsOrgAdminPermission, IsOrgAdminMixin

User = get_user_model()


class TeamPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserOrganizationsListView(generics.ListAPIView):
    """
    List all organizations that the user can manage.
    """
    serializer_class = OrganizationSerializer
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return organizations that the user can manage."""
        return Organization.get_orgs_administered_by_user(self.request.user)


class TeamListCreateView(generics.ListCreateAPIView, IsOrgAdminMixin):
    """
    List teams in an organization or create a new team.
    """
    serializer_class = TeamSerializer
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOrgAdminPermission]
    pagination_class = TeamPagination
    
    def get_queryset(self):
        """Return teams for the specified organization."""
        organization = self.get_organization()
        return Team.objects.filter(organization=organization).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create a team in the specified organization."""
        organization = self.get_organization()
        serializer.save(organization=organization)
    
    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class TeamDetailView(generics.RetrieveUpdateDestroyAPIView, IsOrgAdminMixin):
    """
    Retrieve, update, or delete a team.
    """
    serializer_class = TeamSerializer
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOrgAdminPermission]
    lookup_url_kwarg = 'team_id'
    
    def get_queryset(self):
        """Return teams for the specified organization."""
        organization = self.get_organization()
        return Team.objects.filter(organization=organization)
    
    def get_object(self):
        """Get the team object ensuring it belongs to the organization."""
        organization = self.get_organization()
        team_id = self.kwargs.get('team_id')
        return get_object_or_404(Team, id=team_id, organization=organization)
    
    def perform_update(self, serializer):
        """Update team ensuring organization cannot be changed."""
        organization = self.get_organization()
        serializer.save(organization=organization)
    
    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class TeamMembersView(APIView, IsOrgAdminMixin):
    """
    List team members or add a member to a team.
    """
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOrgAdminPermission]
    
    def get_team(self):
        """Get the team object."""
        organization = self.get_organization()
        team_id = self.kwargs.get('team_id')
        return get_object_or_404(Team, id=team_id, organization=organization)
    
    def get(self, request, org_id, team_id):
        """List all members of a team."""
        team = self.get_team()
        memberships = TeamMembership.objects.filter(team=team).select_related('user')
        serializer = TeamMemberSerializer(memberships, many=True)
        return Response(serializer.data)
    
    def post(self, request, org_id, team_id):
        """Add a member to a team."""
        team = self.get_team()
        serializer = TeamMembershipCreateSerializer(
            data=request.data, 
            context={'team': team}
        )
        if serializer.is_valid():
            user = serializer.validated_data['user_id']
            with transaction.atomic():
                membership = TeamMembership.objects.create(team=team, user=user)
                member_serializer = TeamMemberSerializer(membership)
                return Response(member_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamMemberRemoveView(APIView, IsOrgAdminMixin):
    """
    Remove a member from a team.
    """
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOrgAdminPermission]
    
    def delete(self, request, org_id, team_id, user_id):
        """Remove a member from a team."""
        organization = self.get_organization()
        team = get_object_or_404(Team, id=team_id, organization=organization)
        user = get_object_or_404(User, id=user_id)
        membership = get_object_or_404(TeamMembership, team=team, user=user)
        
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrganizationTeamsView(TeamListCreateView):
    """
    Alternative endpoint for listing teams in an organization.
    This inherits all functionality from TeamListCreateView but only allows GET.
    """
    
    def post(self, request, *args, **kwargs):
        """Disable POST for this endpoint."""
        return Response(
            {"detail": "Method not allowed."}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
