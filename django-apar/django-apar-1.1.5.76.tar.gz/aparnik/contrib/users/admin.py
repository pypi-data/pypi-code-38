# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from aparnik.settings import aparnik_settings
from django.utils.translation import ugettext_lazy as _

from copy import deepcopy
from jalali_date.admin import ModelAdminJalaliMixin
from jalali_date import datetime2jalali


from aparnik.contrib.basemodels.admin import BaseModelAdmin
from aparnik.contrib.users.models import User, DeviceLogin

# Base Function
# foreign key user


def get_first_name(obj):
    return obj.user.first_name


def get_last_name(obj):
    return obj.user.last_name


def get_username(obj):
    return obj.user.username


# Sample usage: get_common_fields('user_obj')+ [rest of fields]
#   => ['user_obj__username', 'user_obj__first_name', 'user_obj__last_name',...]
def get_user_search_fields(field_name):
    field_string = [field_name + '__username', field_name + '__first_name', field_name + '__last_name']
    return field_string


get_last_name.short_description = _('Last Name')
get_username.short_description = _('Mobile')
get_first_name.short_description = _('Name')

# for admin


def get_update_at(obj):
    return datetime2jalali(obj.update_at).strftime(aparnik_settings.JALALI_FORMAT)


get_update_at.admin_order_field = 'update_at'
get_update_at.short_description = 'بروز شده'


def get_last_login(obj):
    if obj.last_login:
        return datetime2jalali(obj.last_login).strftime(aparnik_settings.JALALI_FORMAT)
    return obj.last_login


get_last_login.admin_order_field = 'last_login'
get_last_login.short_description = 'آخرین ورود'


def get_created_at(obj):
    return datetime2jalali(obj.created_at).strftime(aparnik_settings.JALALI_FORMAT)


get_update_at.admin_order_field = 'created_at'
get_update_at.short_description = 'ثبت نام'


class UserAdmin(BaseModelAdmin):
# class UserAdmin(admin.ModelAdmin):
# 'is_superuser', 'groups', 'user_permissions', 'avatar',
#     exclude = [, 'token', 'token_time', 'current_city', ]
    list_display_links = ('username', 'first_name', 'last_name')
    # list_editable = ('username', 'mobile', )
    # inlines = [DocumentFilesInline, ]

    fields = []
    list_display = ['username', 'first_name', 'last_name', 'get_device_login_count', 'limit_device_login', get_last_login, get_created_at, 'created_at']
    list_filter = ['is_staff', 'created_at']
    search_fields = ['username', 'last_name', 'first_name']
    exclude = ['last_login', ]
    raw_id_fields = ['current_city', 'avatar']
    dynamic_raw_id_fields = []

    actions = None

    class Meta:
        model = User

    def __init__(self, *args, **kwargs):
        Klass = UserAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_display.remove('id')
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    # permission
    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False

    def has_add_permission(self, request):
        return True

    def change_view(self, request, object_id, form_url='', extra_context=None):
        ''' customize edit form '''
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = True
        extra_context['show_save'] = True
        extra_context['show_save_and_add_another'] = True  # this not works if has_add_permision is True
        return super(UserAdmin, self).change_view(request, object_id, extra_context=extra_context)

    def get_device_login_count(self, instance):
        return instance.device_login_count()

    get_device_login_count.short_description = 'دستگاه فعال'

    # Removing superuser from staff profile
    def get_fieldsets(self, request, obj=None):
        fieldsets = super(UserAdmin, self).get_fieldsets(request, obj)
        # if not obj:
        #     return fieldsets

        if not request.user.is_superuser:  # or request.user.pk == obj.pk:
            fieldsets = deepcopy(fieldsets)
            for fieldset in fieldsets:
                if 'is_superuser' in fieldset[1]['fields']:
                    if type(fieldset[1]['fields']) == tuple:
                        fieldset[1]['fields'] = list(fieldset[1]['fields'])
                    fieldset[1]['fields'].remove('is_superuser')
                    break

        return fieldsets

    # remove superusers from staff users list
    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(is_superuser=False)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        # Get form from original UserAdmin.
        form = super(UserAdmin, self).get_form(request, obj, **kwargs)
        if 'user_permissions' in form.base_fields:
            user = request.user
            if not user.is_superuser:
                permissions = form.base_fields['user_permissions']
                groups = form.base_fields['groups']
                permissions.queryset = Permission.objects.filter(user=user)
                groups.queryset = Group.objects.filter(user=user)
        return form


class DeviceLoginAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):

    exclude = ('last_login', 'token', 'token_time')
    list_display = ('id', get_username, get_first_name, get_last_name, 'device_id', 'os_version', 'device_model', get_update_at)
    list_display_links = None
    # list_filter = ('is_staff',)
    # list_editable = ('username', 'mobile', )
    search_fields = get_user_search_fields('user') + ['device_id']
    readonly_fields = ( )
    # inlines = [DocumentFilesInline, ]

    actions = None

    # class Meta:
    #     model = User

    # # permission
    # def has_delete_permission(self, request, obj=None):
    #     # Disable delete
    #     return False
    #
    # def has_add_permission(self, request):
    #     return False
    #
    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     ''' customize edit form '''
    #     extra_context = extra_context or {}
    #     extra_context['show_save_and_continue'] = False
    #     extra_context['show_save'] = False
    #     extra_context['show_save_and_add_another'] = False  # this not works if has_add_permision is True
    #     return super(UserAdmin, self).change_view(request, object_id, extra_context=extra_context)


if aparnik_settings.USER_IS_SHOW_ADMIN_PANEL:
    admin.site.register(User, UserAdmin)
    admin.site.register(DeviceLogin, DeviceLoginAdmin)
# Now register the new UserAdmin...
# admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
# admin.site.unregister(Group)