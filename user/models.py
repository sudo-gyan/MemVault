from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time when the user was created")
    
    # Set username as the field used for authentication
    USERNAME_FIELD = 'username'
    
    def __str__(self):
        return self.username

class Organization(models.Model):
    """Organization model that can nest and contain teams."""
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='administered_orgs',
        help_text="Admin user who can manage this organization and its teams"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            # For filtering by admin (heavily used in permissions and views)
            models.Index(fields=['admin']),
        ]
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def is_admin(self, user):
        """Check if a user is an admin of this organization."""
        return self.admin == user
    
    
    @classmethod
    def get_orgs_administered_by_user(cls, user):
        """Get all organizations where the user is an admin"""
        return cls.objects.filter(admin=user)
    
    def __str__(self):
        return self.name


class Team(models.Model):
    """Team model that belongs to an organization."""
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE,
        related_name='teams'
    )
    members = models.ManyToManyField(
        User, 
        through='TeamMembership',
        related_name='teams'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['name', 'organization']
        indexes = [
            # For ordering by creation date
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class TeamMembership(models.Model):
    """Intermediate model for User-Team many-to-many relationship."""
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'team']
        indexes = [
            # For authorization checks
            models.Index(fields=['user', 'team']),
        ]

