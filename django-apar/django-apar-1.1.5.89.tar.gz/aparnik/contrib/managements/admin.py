# -*- coding: utf-8 -*-


from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from aparnik.contrib.basemodels.admin import BaseModelAdmin
from aparnik.contrib.managements.models import Management, FieldList, ManagementActions, ManagementRoles, \
    ManagementPermission
from .forms import ManagementForm, FieldListForm


# Register your models here.
class ManagementRolesAdmin(BaseModelAdmin):
    fields = ['title', 'management_obj']
    list_display = ['title']
    list_filter = []
    search_fields = []
    exclude = []
    save_as = True

    def __init__(self, *args, **kwargs):
        Klass = ManagementRolesAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude

    class Meta:
        model = ManagementRoles


class ManagementAdmin(BaseModelAdmin):
    change_list_template = "update-management.html"
    fields = ['group', 'application', 'fields', 'start_date', 'end_date']
    list_display = ['group', 'application', 'start_date', 'end_date']
    list_filter = ['group']
    search_fields = ['group__name', 'fields__id', 'application']
    raw_id_fields = []
    dynamic_raw_id_fields = ['group', 'fields']
    exclude = []
    save_as = True
    form = ManagementForm

    def __init__(self, *args, **kwargs):
        Klass = ManagementAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude

    def get_urls(self):
        urls = super(ManagementAdmin, self).get_urls()
        my_urls = [
            url(r'^update-management/$', self.admin_site.admin_view(self.update_management))
        ]
        return my_urls + urls

    def update_management(self, request):
        group_id = int(request.POST['group_id'])
        try:
            FieldList.objects.update_fields(group_id)
            Management.objects.update_apps(group_id)
        except:
            self.message_user(request, _("Aparnik management group id does not exist ") + str(group_id),
                              level=messages.ERROR)
            return HttpResponseRedirect("../")

        self.message_user(request, _("Aparnik management data updated successfully for group id ") + str(group_id))
        return HttpResponseRedirect("../")

    def save_model(self, request, obj, form, change):
        obj.is_superuser = request.user.is_superuser
        super(ManagementAdmin, self).save_model(request, obj, form, change)

    class Meta:
        model = Management


class FieldListAdmin(BaseModelAdmin):
    fields = ['model', 'name', 'group', 'actions', 'permission', 'is_enable', 'is_sharable', 'default']
    list_display = ['name', 'model', 'group', 'default', 'is_enable']
    list_filter = ['is_enable', 'group', 'model', ]
    search_fields = ['name', 'model']
    exclude = []
    save_as = True
    form = FieldListForm
    actions = ['make_enable', 'make_disable']

    def make_enable(self, request, queryset):
        rows_updated = queryset.update(is_enable=True)
        if rows_updated == 1:
            message_bit = "1 field was"
        else:
            message_bit = "%s fields were" % rows_updated
        self.message_user(request, _("%s successfully marked as enabled.") % message_bit)

    make_enable.short_description = _("Mark selected fields as enabled")

    def make_disable(self, request, queryset):
        rows_updated = queryset.update(is_enable=False)

        if rows_updated == 1:
            message_bit = "1 field was"
        else:
            message_bit = "%s fields were" % rows_updated

        self.message_user(request, _("%s successfully marked as disabled.") % message_bit)

    make_disable.short_description = _("Mark selected fields as disabled")

    def __init__(self, *args, **kwargs):
        Klass = FieldListAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude

    class Meta:
        model = FieldList


class ManagementActionsAdmin(BaseModelAdmin):
    fields = ['title', 'description']
    list_display = ['title', 'description']
    list_filter = []
    search_fields = []
    exclude = []
    save_as = True

    def __init__(self, *args, **kwargs):
        Klass = ManagementActionsAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude

    def save_model(self, request, obj, form, change):
        obj.is_superuser = request.user.is_superuser
        super(ManagementActionsAdmin, self).save_model(request, obj, form, change)

    class Meta:
        model = ManagementActions


class ManagementPermissionAdmin(BaseModelAdmin):
    fields = ['title', 'description']
    list_display = ['title', 'description']
    list_filter = []
    search_fields = []
    exclude = []
    save_as = True

    def __init__(self, *args, **kwargs):
        Klass = ManagementPermissionAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude

    class Meta:
        model = ManagementPermission


# Change to users admin class
admin.site.register(Management, ManagementAdmin)
admin.site.register(ManagementPermission, ManagementPermissionAdmin)
admin.site.register(FieldList, FieldListAdmin)
admin.site.register(ManagementRoles, ManagementRolesAdmin)
admin.site.register(ManagementActions, ManagementActionsAdmin)
