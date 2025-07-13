from django.contrib import admin
from .models import UserMemory, TeamMemory, OrganizationMemory


@admin.register(UserMemory)
class UserMemoryAdmin(admin.ModelAdmin):
    """Admin interface for UserMemory model."""
    list_display = ['id', 'user', 'content_preview', 'processing_status', 'is_processed', 'created_at']
    list_filter = ['processing_status', 'is_processed', 'created_at']
    search_fields = ['user__username', 'content']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        """Show a preview of the content."""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(TeamMemory)
class TeamMemoryAdmin(admin.ModelAdmin):
    """Admin interface for TeamMemory model."""
    list_display = ['id', 'team', 'content_preview', 'processing_status', 'is_processed', 'created_at']
    list_filter = ['processing_status', 'is_processed', 'created_at']
    search_fields = ['team__name', 'team__organization__name', 'content']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        """Show a preview of the content."""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(OrganizationMemory)
class OrganizationMemoryAdmin(admin.ModelAdmin):
    """Admin interface for OrganizationMemory model."""
    list_display = ['id', 'organization', 'content_preview', 'processing_status', 'is_processed', 'created_at']
    list_filter = ['processing_status', 'is_processed', 'created_at']
    search_fields = ['organization__name', 'content']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        """Show a preview of the content."""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
