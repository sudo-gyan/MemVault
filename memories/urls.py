from django.urls import path
from .views import (
    UserMemoryListCreateView,
    UserMemoryDetailView,
    TeamMemoryListCreateView,
    TeamMemoryDetailView,
    OrganizationMemoryListCreateView,
    OrganizationMemoryDetailView,
)

urlpatterns = [
    # User memory endpoints
    path(
        "users/me/", UserMemoryListCreateView.as_view(), name="user-memory-list-create"
    ),
    path(
        "users/me/<int:memory_id>/",
        UserMemoryDetailView.as_view(),
        name="user-memory-detail",
    ),
    # Team memory endpoints
    path(
        "teams/<int:team_id>/",
        TeamMemoryListCreateView.as_view(),
        name="team-memory-list-create",
    ),
    path(
        "teams/<int:team_id>/<int:memory_id>/",
        TeamMemoryDetailView.as_view(),
        name="team-memory-detail",
    ),
    # Organization memory endpoints
    path(
        "orgs/<int:org_id>/",
        OrganizationMemoryListCreateView.as_view(),
        name="organization-memory-list-create",
    ),
    path(
        "orgs/<int:org_id>/<int:memory_id>/",
        OrganizationMemoryDetailView.as_view(),
        name="organization-memory-detail",
    ),
]
