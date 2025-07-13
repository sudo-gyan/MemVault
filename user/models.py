from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time when the user was created")
    
    # Set username as the field used for authentication
    USERNAME_FIELD = 'username'
    
    def __str__(self):
        return self.username
