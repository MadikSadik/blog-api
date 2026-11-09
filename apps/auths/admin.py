from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import BooleanRadioFilter
from unfold.decorators import action, display
from unfold.forms import AdminPasswordChangeForm

from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count, QuerySet
from django.http import HttpRequest

from apps.auths.constants import ACTIVE_KEY, INACTIVE_KEY, REGULAR_KEY, STAFF_KEY
from apps.auths.forms import UserChangeForm, UserCreationForm
from apps.auths.models import User

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    ordering = ('email',)
    list_display = ('user_header', 'active_label', 'staff_label', 'posts_count')
    list_filter = [
        ('is_active', BooleanRadioFilter),
        ('is_staff', BooleanRadioFilter),
    ]
    list_filter_submit = True
    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login',)
    actions = ['activate_users', 'deactivate_users']

    fieldsets = (
        (
            'Personal info',
            {'classes': ['tab'], 'fields': ('email', 'password', 'first_name', 'last_name')},
        ),
        (
            'Permissions',
            {
                'classes': ['tab'],
                'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            },
        ),
        ('Important dates', {'classes': ['tab'], 'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
            },
        ),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).annotate(posts_total=Count('post'))

    @display(description='User', header=True)
    def user_header(self, obj: User) -> list[str]:
        initials = (obj.first_name[:1] + obj.last_name[:1]).upper()
        return [f'{obj.first_name} {obj.last_name}', obj.email, initials]

    @display(
        description='Active',
        ordering='is_active',
        label={ACTIVE_KEY: 'success', INACTIVE_KEY: 'danger'},
    )
    def active_label(self, obj: User) -> tuple[str, str]:
        if obj.is_active:
            return ACTIVE_KEY, 'Active'
        return INACTIVE_KEY, 'Inactive'

    @display(
        description='Staff',
        ordering='is_staff',
        label={STAFF_KEY: 'info', REGULAR_KEY: 'warning'},
    )
    def staff_label(self, obj: User) -> tuple[str, str]:
        if obj.is_staff:
            return STAFF_KEY, 'Staff'
        return REGULAR_KEY, 'Regular'

    @display(description='Posts', ordering='posts_total')
    def posts_count(self, obj: User) -> int:
        return obj.posts_total

    @action(description='Activate selected users')
    def activate_users(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users activated.')

    @action(description='Deactivate selected users')
    def deactivate_users(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.exclude(pk=request.user.pk).update(is_active=False)
        self.message_user(request, f'{updated} users deactivated.')


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
