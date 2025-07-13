from rest_framework import permissions
from django.db.models import Q
from user.models import Organization, Team, TeamMembership


class UserMemoryPermission(permissions.BasePermission):
    """
    Permission for user memory endpoints.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """User can only access their own memories."""
        return obj.user == request.user


class TeamMemoryPermission(permissions.BasePermission):
    """
    Permission for team memory endpoints.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated and can access the team."""
        if not (request.user and request.user.is_authenticated):
            return False
        
        team_id = view.kwargs.get('team_id')
        if not team_id:
            return True  # For list views, filtering will handle this
        
        try:
            team = Team.objects.get(id=team_id)
            # Check if user is member of the team or admin of the organization
            return (
                TeamMembership.objects.filter(user=request.user, team=team).exists() or
                team.organization.admin == request.user
            )
        except Team.DoesNotExist:
            return False
    
    def has_object_permission(self, request, view, obj):
        """User must be a team member or org admin."""
        user = request.user
        
        # Check if user is member of the team
        if TeamMembership.objects.filter(user=user, team=obj.team).exists():
            return True
        
        # Check if user is admin of the organization
        return obj.team.organization.admin == user


class OrganizationMemoryPermission(permissions.BasePermission):
    """
    Permission for organization memory endpoints.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated and can access the organization."""
        if not (request.user and request.user.is_authenticated):
            return False
        
        org_id = view.kwargs.get('org_id')
        if not org_id:
            return True  # For list views, filtering will handle this
        
        try:
            organization = Organization.objects.get(id=org_id)
            # Check if user is admin of the organization or member of any team
            return (
                organization.admin == request.user or
                TeamMembership.objects.filter(
                    user=request.user,
                    team__organization=organization
                ).exists()
            )
        except Organization.DoesNotExist:
            return False
    
    def has_object_permission(self, request, view, obj):
        """User must be org admin or member of the organization."""
        user = request.user
        
        # Check if user is admin of the organization
        if obj.organization.admin == user:
            return True
        
        # Check if user is member of any team in the organization
        return TeamMembership.objects.filter(
            user=user,
            team__organization=obj.organization
        ).exists()
