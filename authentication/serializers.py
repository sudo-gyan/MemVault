from rest_framework import serializers
from .models import APIKey


class APIKeySerializer(serializers.ModelSerializer):
    """
    Serializer for APIKey model.

    Used for displaying API key information with masked keys for security.
    """

    masked_primary_key = serializers.SerializerMethodField()
    masked_secondary_key = serializers.SerializerMethodField()

    class Meta:
        model = APIKey
        fields = [
            "id",
            "masked_primary_key",
            "masked_secondary_key",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_masked_primary_key(self, obj):
        """Return masked primary key for security."""
        if obj.primary_key:
            return f"{obj.primary_key[:10]}...{obj.primary_key[-4:]}"
        return None

    def get_masked_secondary_key(self, obj):
        """Return masked secondary key for security."""
        if obj.secondary_key:
            return f"{obj.secondary_key[:10]}...{obj.secondary_key[-4:]}"
        return None


class APIKeyFullSerializer(serializers.ModelSerializer):
    """
    Serializer for APIKey model with full key display.

    Used when generating or regenerating keys to show the full key value.
    WARNING: Only use this for key generation/regeneration responses.
    """

    class Meta:
        model = APIKey
        fields = ["id", "primary_key", "secondary_key", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class KeyRegenerationSerializer(serializers.Serializer):
    """
    Serializer for key regeneration responses.

    Returns only the newly generated key.
    """

    key = serializers.CharField(read_only=True)
    key_type = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)
