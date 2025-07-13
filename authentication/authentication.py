from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.db import models
from .models import APIKey

User = get_user_model()


class APIKeyAuthentication(BaseAuthentication):
    """
    Custom authentication class for API key based authentication.
    
    This authentication class checks for API keys in X-API-Key
    """
    
    def authenticate(self, request):
        """
        Authenticate the request using API key.

        Returns:
            tuple: (user, api_key) if authentication succeeds
            None: if authentication fails or no API key provided
        """
        api_key = request.META.get('HTTP_X_API_KEY')
        
        # If no API key found in header, return None
        if not api_key:
            return None
        
        return self.authenticate_credentials(api_key)
    
    def authenticate_credentials(self, key):
        """
        Authenticate the API key against the database.
        
        Args:
            key (str): The API key to authenticate
            
        Returns:
            tuple: (user, api_key) if authentication succeeds
            
        Raises:
            AuthenticationFailed: If the API key is invalid or user is inactive
        """
        try:
            # Find APIKey object where the key matches either primary or secondary key
            api_key_obj = APIKey.objects.select_related('user').get(
                models.Q(primary_key=key) | models.Q(secondary_key=key)
            )
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')
        
        user = api_key_obj.user
        
        if not user.is_active:
            raise AuthenticationFailed('User account is disabled')
        
        return (user, api_key_obj)
