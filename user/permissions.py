from rest_framework import permissions
from django.shortcuts import get_object_or_404
from .models import Organization


class IsOrgAdminPermission(permissions.BasePermission):
    """
    Custom permission to check if user is an admin of the organization.
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated and has admin permission for the organization.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get org_id from URL kwargs
        org_id = view.kwargs.get('org_id')
        if not org_id:
            return True  # Let other permissions handle this case
        
        try:
            organization = Organization.objects.get(id=org_id)
            user_managed_orgs = Organization.get_orgs_administered_by_user(request.user)
            return organization in user_managed_orgs
        except Organization.DoesNotExist:
            return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to access the specific object.
        """
        # For Team objects, check if user can manage the team's organization
        if hasattr(obj, 'organization'):
            user_managed_orgs = Organization.get_orgs_administered_by_user(request.user)
            return obj.organization in user_managed_orgs
        
        # For Organization objects, check if user can manage this organization
        if isinstance(obj, Organization):
            user_managed_orgs = Organization.get_orgs_administered_by_user(request.user)
            return obj in user_managed_orgs
        
        return False


class IsOrgAdminMixin:
    """
    Mixin to add organization admin checking functionality to views.
    """
    
    def get_organization(self):
        """Get the organization from URL kwargs."""
        org_id = self.kwargs.get('org_id')
        if org_id:
            return get_object_or_404(Organization, id=org_id)
        return None
    
    def check_org_admin_permission(self, organization=None):
        """Check if user has admin permission for the organization."""
        if not organization:
            organization = self.get_organization()
        
        if not organization:
            return False
            
        user_managed_orgs = Organization.get_orgs_administered_by_user(self.request.user)
        return organization in user_managed_orgs
