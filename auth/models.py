import secrets
from django.db import models
from django.conf import settings


class APIKey(models.Model):
    """
    APIKey model for managing user API keys.
    
    Each user can have primary and secondary API keys for authentication.
    Keys can be regenerated individually while maintaining access.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='api_keys'
    )
    primary_key = models.CharField(max_length=64, unique=True)
    secondary_key = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_apikey'
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
        indexes = [
            models.Index(fields=['primary_key']),
            models.Index(fields=['secondary_key']),
            models.Index(fields=['user']),
        ]
    
    def save(self, *args, **kwargs):
        """Generate keys if they don't exist."""
        if not self.primary_key:
            self.primary_key = self.generate_key()
        if not self.secondary_key:
            self.secondary_key = self.generate_key()
        super().save(*args, **kwargs)
    
    def regenerate_primary_key(self):
        """Regenerate only the primary key."""
        self.primary_key = self.generate_key()
        self.save(update_fields=['primary_key', 'updated_at'])
        return self.primary_key
    
    def regenerate_secondary_key(self):
        """Regenerate only the secondary key."""
        self.secondary_key = self.generate_key()
        self.save(update_fields=['secondary_key', 'updated_at'])
        return self.secondary_key
    
    def is_valid_key(self, key):
        """Check if the provided key matches either primary or secondary key."""
        return key == self.primary_key or key == self.secondary_key
    
    @classmethod
    def generate_key(cls):
        """Generate a secure API key."""
        return "MEM0_" + secrets.token_urlsafe(48)
    
    def __str__(self):
        return f"API Keys for {self.user.username}"
