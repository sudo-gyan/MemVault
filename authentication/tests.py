from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import APIKey

User = get_user_model()


class APIKeySignalTestCase(TestCase):
    """Test cases for API key creation signals."""
    
    def test_api_key_created_on_user_creation(self):
        """Test that API keys are automatically created when a new user is created."""
        # Create a new user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Check that API keys were automatically created
        self.assertTrue(APIKey.objects.filter(user=user).exists())
        
        # Get the API key object
        api_key = APIKey.objects.get(user=user)
        
        # Verify that both primary and secondary keys are generated
        self.assertIsNotNone(api_key.primary_key)
        self.assertIsNotNone(api_key.secondary_key)
        self.assertTrue(api_key.primary_key.startswith('MEM0_'))
        self.assertTrue(api_key.secondary_key.startswith('MEM0_'))
        
        # Verify keys are different
        self.assertNotEqual(api_key.primary_key, api_key.secondary_key)
    
    def test_api_key_not_recreated_on_user_update(self):
        """Test that API keys are not recreated when an existing user is updated."""
        # Create a new user (this should trigger API key creation)
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Get the original API key
        original_api_key = APIKey.objects.get(user=user)
        original_primary = original_api_key.primary_key
        original_secondary = original_api_key.secondary_key
        
        # Update the user
        user.email = 'updated@example.com'
        user.save()
        
        # Verify that the API key still exists and hasn't changed
        updated_api_key = APIKey.objects.get(user=user)
        self.assertEqual(updated_api_key.primary_key, original_primary)
        self.assertEqual(updated_api_key.secondary_key, original_secondary)
        
        # Verify there's still only one API key for this user
        self.assertEqual(APIKey.objects.filter(user=user).count(), 1)
