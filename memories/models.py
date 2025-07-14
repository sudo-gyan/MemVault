from django.db import models
from django.forms import ValidationError
from user.models import User, Team, Organization


class BaseMemory(models.Model):
    """Base memory model with common fields and functionality."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    
    # Memory content
    content = models.TextField(help_text="The actual memory content")
    mem0_memory_id = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text="ID from mem0 ai"
    )
    
    # Status and error handling
    status = models.CharField(
        max_length=50, 
        choices=STATUS_CHOICES,
        default='pending'
    )
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['content'], name='%(class)s_content_search'),
        ]

    def mark_as_processing(self):
        """Mark memory as being processed."""
        self.status = 'processing'
        self.save(update_fields=['status', 'updated_at'])

    def mark_as_completed(self):
        """Mark memory as successfully processed."""
        self.status = 'completed'
        self.error_message = ''
        self.save(update_fields=['status', 'error_message', 'updated_at'])

    def mark_as_failed(self, error_message=''):
        """Mark memory as failed with optional error message."""
        self.status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message', 'updated_at'])


class UserMemory(BaseMemory):
    """Memory specific to a user."""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='memories'
    )

    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"Memory for {self.user.username}"

    @property
    def scope(self):
        return 'user'

    @property
    def owner(self):
        return self.user


class TeamMemory(BaseMemory):
    """Memory specific to a team."""
    
    team = models.ForeignKey(
        Team, 
        on_delete=models.CASCADE,
        related_name='memories'
    )

    class Meta:
        indexes = [
            models.Index(fields=['team', '-created_at']),
            models.Index(fields=['team', 'status']),
        ]

    def __str__(self):
        return f"Memory for team {self.team.name}"

    @property
    def scope(self):
        return 'team'

    @property
    def owner(self):
        return self.team


class OrganizationMemory(BaseMemory):
    """Memory specific to an organization."""
    
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE,
        related_name='memories'
    )

    class Meta:
        indexes = [
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['organization', 'status']),
        ]

    def __str__(self):
        return f"Memory for org {self.organization.name}"

    @property
    def scope(self):
        return 'organization'

    @property
    def owner(self):
        return self.organization
