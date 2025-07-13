from django.contrib import admin
from django.utils.html import format_html
from .models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """
    Admin interface for APIKey model.
    
    Provides functionality to view and manage API keys with actions
    to regenerate keys individually.
    """
    list_display = ('user', 'masked_primary_key', 'masked_secondary_key', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username',)
    readonly_fields = ('primary_key', 'secondary_key', 'created_at', 'updated_at')
    ordering = ('-created_at',)

        
    def masked_primary_key(self, obj):
        """Display masked primary key for security."""
        if obj.primary_key:
            return f"{obj.primary_key[:10]}...{obj.primary_key[-4:]}"
        return "Not set"
    masked_primary_key.short_description = "Primary Key"
    
    def masked_secondary_key(self, obj):
        """Display masked secondary key for security."""
        if obj.secondary_key:
            return f"{obj.secondary_key[:10]}...{obj.secondary_key[-4:]}"
        return "Not set"
    masked_secondary_key.short_description = "Secondary Key"
