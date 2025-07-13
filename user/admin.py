from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class UserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class UserChangeForm(UserChangeForm):
    
    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    UserAdmin that includes the created_at field and maintains
    all the default Django user admin functionality.
    """
    form = UserChangeForm
    add_form = UserCreationForm
    
    # Fields to display in the admin list view
    list_display = ('username', 'first_name', 'last_name', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'created_at')
    search_fields = ('username', 'first_name', 'last_name')
    ordering = ('-created_at',)
        
    # Fieldsets for the change user form
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('User info', {'fields': ('first_name', 'last_name',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Timestamp', {'fields': ('last_login', 'created_at')}),
    )
    
    # Fields for the add user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    

    # Make created_at read-only since it's auto-generated
    readonly_fields = ('created_at',)
