from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import APIKey


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_api_key_for_user(sender, instance, created, **kwargs):
    """
    Signal to automatically create API keys when a new user is created.
    
    Args:
        sender: The User model class
        instance: The actual user instance that was saved
        created: Boolean indicating if this is a new user (True) or an update (False)
        **kwargs: Additional keyword arguments
    """
    if created:
        # Only create API keys for newly created users
        APIKey.objects.create(user=instance)