from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = (
        'id', 'username', 'first_name', 'email', 'phone',
        'birth_date', 'account_status', 'is_staff', 'date_joined'
    )
    list_filter = (
        'account_status', 'is_staff', 'is_superuser', 'is_active',
        'groups', 'date_joined'
    )
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    ordering = ('-date_joined',)

    actions = ['block_users', 'unblock_users', 'set_on_hold']

    fieldsets = UserAdmin.fieldsets + (
        (_('Дополнительная информация'), {
            'fields': ('phone', 'birth_date', 'account_status')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('Доп. информация'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'birth_date', 'account_status')
        }),
    )

    filter_horizontal = ('groups', 'user_permissions')

    def block_users(self, request, queryset):
        queryset.update(account_status='blocked', is_active=False)
        self.message_user(request, f'Заблокировано {queryset.count()} пользователей.')
    block_users.short_description = 'Заблокировать выбранных пользователей'

    def unblock_users(self, request, queryset):
        queryset.update(account_status='active', is_active=True)
        self.message_user(request, f'Разблокировано {queryset.count()} пользователей.')
    unblock_users.short_description = 'Разблокировать выбранных пользователей'

    def set_on_hold(self, request, queryset):
        queryset.update(account_status='on_hold', is_active=False)
        self.message_user(request, f'{queryset.count()} пользователей переведены в статус "На удержании".')
    set_on_hold.short_description = 'Перевести на удержание'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('password',)
        return ()

admin.site.register(CustomUser, CustomUserAdmin)