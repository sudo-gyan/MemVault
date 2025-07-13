from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from django.shortcuts import get_object_or_404
from .models import APIKey
from .serializers import APIKeySerializer, APIKeyFullSerializer, KeyRegenerationSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_api_keys(request):
    """
    Get the current user's API keys (masked for security).
    
    Returns:
        - 200: API keys with masked values
        - 404: No API keys found for user
    """
    try:
        api_key = APIKey.objects.get(user=request.user)
        serializer = APIKeySerializer(api_key)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except APIKey.DoesNotExist:
        return Response(
            {'error': 'No API keys found for this user'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_api_keys(request):
    """
    Generate new API keys for the current user.
    
    Creates a new APIKey object if one doesn't exist, or regenerates both keys if it does.
    
    Returns:
        - 201: New API keys created
        - 200: Existing API keys regenerated
    """
    api_key, created = APIKey.objects.get_or_create(user=request.user)
    
    if not created:
        # If APIKey already exists, regenerate both keys
        api_key.primary_key = APIKey.generate_key()
        api_key.secondary_key = APIKey.generate_key()
        api_key.save(update_fields=['primary_key', 'secondary_key', 'updated_at'])
        message = "API keys regenerated successfully"
        status_code = status.HTTP_200_OK
    else:
        message = "API keys generated successfully"
        status_code = status.HTTP_201_CREATED
    
    serializer = APIKeyFullSerializer(api_key)
    response_data = serializer.data
    response_data['message'] = message
    
    return Response(response_data, status=status_code)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_primary_key(request):
    """
    Regenerate only the primary API key for the current user.
    
    Returns:
        - 200: Primary key regenerated successfully
        - 404: No API keys found for user
    """
    try:
        api_key = APIKey.objects.get(user=request.user)
        new_key = api_key.regenerate_primary_key()
        
        serializer = KeyRegenerationSerializer({
            'key': new_key,
            'key_type': 'primary',
            'message': 'Primary API key regenerated successfully'
        })
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    except APIKey.DoesNotExist:
        return Response(
            {'error': 'No API keys found for this user'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_secondary_key(request):
    """
    Regenerate only the secondary API key for the current user.
    
    Returns:
        - 200: Secondary key regenerated successfully
        - 404: No API keys found for user
    """
    try:
        api_key = APIKey.objects.get(user=request.user)
        new_key = api_key.regenerate_secondary_key()
        
        serializer = KeyRegenerationSerializer({
            'key': new_key,
            'key_type': 'secondary',
            'message': 'Secondary API key regenerated successfully'
        })
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    except APIKey.DoesNotExist:
        return Response(
            {'error': 'No API keys found for this user'}, 
            status=status.HTTP_404_NOT_FOUND
        )
