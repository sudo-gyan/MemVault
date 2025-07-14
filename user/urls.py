from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    # Organization management
    path(
        "organizations/",
        views.UserOrganizationsListView.as_view(),
        name="user_organizations",
    ),
    # Team management endpoints
    path(
        "organizations/<int:org_id>/teams/",
        views.TeamListCreateView.as_view(),
        name="team_list_create",
    ),
    path(
        "organizations/<int:org_id>/teams/<int:team_id>/",
        views.TeamDetailView.as_view(),
        name="team_detail",
    ),
    # Team member management endpoints
    path(
        "organizations/<int:org_id>/teams/<int:team_id>/members/",
        views.TeamMembersView.as_view(),
        name="team_members",
    ),
    path(
        "organizations/<int:org_id>/teams/<int:team_id>/members/<int:user_id>/",
        views.TeamMemberRemoveView.as_view(),
        name="team_member_remove",
    ),
    # Alternative endpoint for listing teams
    path(
        "organizations/<int:org_id>/teams/list/",
        views.OrganizationTeamsView.as_view(),
        name="organization_teams",
    ),
]
