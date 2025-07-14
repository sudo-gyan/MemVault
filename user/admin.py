from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Organization, Team, TeamMembership


class UserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name")


class UserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    UserAdmin that includes the created_at field and maintains
    all the default Django user admin functionality.
    """

    form = UserChangeForm
    add_form = UserCreationForm

    # Fields to display in the admin list view
    list_display = (
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "created_at",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "created_at")
    search_fields = ("username", "first_name", "last_name")
    ordering = ("-created_at",)

    # Fieldsets for the change user form
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "User info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Timestamp", {"fields": ("last_login", "created_at")}),
    )

    # Fields for the add user form
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    # Make created_at read-only since it's auto-generated
    readonly_fields = ("created_at",)


class TeamMembershipInline(admin.TabularInline):
    """Inline admin for team memberships."""

    model = TeamMembership
    extra = 0
    readonly_fields = ("joined_at",)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin interface for Organization model."""

    list_display = ("name", "admin", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("name", "admin")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin interface for Team model."""

    list_display = (
        "name",
        "organization",
        "get_member_count",
        "created_at",
        "updated_at",
    )
    list_filter = ("organization", "created_at", "updated_at")
    search_fields = ("name", "organization__name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [TeamMembershipInline]

    fieldsets = (
        (None, {"fields": ("name", "description", "organization")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def get_member_count(self, obj):
        """Get the number of members in the team."""
        return obj.members.count()

    get_member_count.short_description = "Member Count"


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    """Admin interface for TeamMembership model."""

    list_display = ("user", "team", "joined_at")
    list_filter = ("team__organization", "joined_at")
    search_fields = ("user__username", "team__name")
    ordering = ("-joined_at",)
    readonly_fields = ("joined_at",)

    fieldsets = (
        (None, {"fields": ("user", "team")}),
        ("Timestamps", {"fields": ("joined_at",)}),
    )
