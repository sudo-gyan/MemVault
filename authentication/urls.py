from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # API Key management endpoints
    path('api-keys/', views.get_api_keys, name='get_api_keys'),
    path('api-keys/generate/', views.generate_api_keys, name='generate_api_keys'),
    path('api-keys/regenerate-primary/', views.regenerate_primary_key, name='regenerate_primary_key'),
    path('api-keys/regenerate-secondary/', views.regenerate_secondary_key, name='regenerate_secondary_key'),
]
