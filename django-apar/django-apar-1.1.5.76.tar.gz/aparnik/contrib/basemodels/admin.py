# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin.options import StackedInline, TabularInline
from django.apps import apps

from jalali_date.admin import ModelAdminJalaliMixin
from dynamic_raw_id.admin import DynamicRawIDMixin
from aparnik.contrib.managements.models import ManagementActions, FieldList
from .models import BaseModel


# from questionsanswer.models import QA, Like

class BaseAdmin(ModelAdminJalaliMixin, DynamicRawIDMixin, admin.ModelAdmin):
    fields = []
    list_filter = []
    list_display = []
    search_fields = []
    exclude = []
    raw_id_fields = []
    dynamic_raw_id_fields = []


class BaseModelStackedInline(StackedInline):
    exclude = ['review_average', 'visit_count']


class BaseModelTabularInline(TabularInline):
    exclude = ['review_average', 'visit_count']


class BaseModelAdmin(BaseAdmin):
    fields = []
    list_display = ['id', ]
    list_filter = []
    search_fields = []
    exclude = ['review_average', 'update_needed']
    raw_id_fields = []
    dynamic_raw_id_fields = []
    readonly_fields = []
    allowed_actions = []
    save_as = True

    def __init__(self, *args, **kwargs):
        Klass = BaseModelAdmin
        Klass_parent = BaseAdmin

        super(Klass, self).__init__(*args, **kwargs)
        if issubclass(self.model, BaseModel):
            self.fields = self.fields + ['is_show_only_for_super_user', 'tags', 'sort']
            self.list_display = self.list_display + ['sort']

        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = BaseModel

    def get_queryset(self, request):
        qs = super(BaseModelAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            if issubclass(self.model, BaseModel):
                return qs.filter(is_show_only_for_super_user=False)
        return qs

    def get_action_choices(self, request, default_choices=[]):
        if request.user.is_superuser:
            return super(BaseModelAdmin, self).get_action_choices(request,
                                                                  default_choices=self.allowed_actions) + self.get_allowed_actions(
                request)
        else:
            return self.get_allowed_actions(request)

    def get_form(self, request, obj=None, **kwargs):
        form = super(BaseModelAdmin, self).get_form(request, obj=obj, **kwargs)

        editable_fields = self.get_editable_fields(self, request)
        allowed_fields = self.get_allowed_permissions(request)
        if editable_fields == 'all':
            return form
        else:
            try:
                if obj:
                    for field in allowed_fields:
                        if field not in editable_fields:
                            form.base_fields[field].disabled = True
                if obj is None:
                    for field in allowed_fields:
                        if field not in editable_fields:
                            form.base_fields[field].disabled = True
            except:
                pass

        return form

    def get_fieldsets(self, request, obj=None):
        allowed_fields = self.get_allowed_permissions(request)

        if allowed_fields == 'all':
            return super(BaseModelAdmin, self).get_fieldsets(request, obj=obj)
        else:
            field_sets = []

            for permits in super(BaseModelAdmin, self).get_fieldsets(request, obj=obj):
                for permit in permits[1]['fields']:
                    if permit in allowed_fields:
                        field_sets.append(permit)

            return [(None, {'fields': field_sets})]

    def get_list_display(self, request, obj=None):
        allowed_fields = self.get_allowed_permissions(request)

        if allowed_fields == 'all':
            return super(BaseModelAdmin, self).get_list_display(request)
        else:
            list_display = []

            for permit in super(BaseModelAdmin, self).get_list_display(request):
                if permit in allowed_fields:
                    list_display.append(permit)

        return list_display

    def get_list_filter(self, request, obj=None):
        allowed_fields = self.get_allowed_permissions(request)

        if allowed_fields == 'all':
            return super(BaseModelAdmin, self).get_list_filter(request)
        else:
            list_filter = []

            for permit in super(BaseModelAdmin, self).get_list_filter(request):
                if permit in allowed_fields:
                    list_filter.append(permit)

        return list_filter

    def get_search_fields(self, request, obj=None):
        allowed_fields = self.get_allowed_permissions(request)

        if allowed_fields == 'all':
            return super(BaseModelAdmin, self).get_search_fields(request)
        else:
            search_fields = []

            for permit in super(BaseModelAdmin, self).get_search_fields(request):
                if permit in allowed_fields:
                    search_fields.append(permit)

        return search_fields

    def get_allowed_permissions(self, request, model_name=None, active=True):
        group = list(request.user.groups.values_list('id', flat=True).all())
        current_app = request.resolver_match.func.model_admin.model._meta.app_label
        if not model_name:
            model_name = request.resolver_match.func.model_admin.model._meta.object_name

        view_permissions = list(
            FieldList.objects.filter(management__group__in=group, group_id__in=group,
                                     management__application=current_app, model=model_name,
                                     is_enable=active
                                     , permission__title__contains='view').values_list('name', flat=True))

        if request.user.is_superuser:
            view_permissions = 'all'

        return view_permissions

    @staticmethod
    def get_editable_fields(self, request):
        group = list(request.user.groups.values_list('id', flat=True).all())
        current_app = request.resolver_match.func.model_admin.model._meta.app_label
        model_name = request.resolver_match.func.model_admin.model._meta.object_name

        edit_permissions = list(
            FieldList.objects.filter(management__group__in=group, management__application=current_app, model=model_name,
                                     is_enable=True
                                     , permission__title__contains='edit').values_list('name', flat=True))

        if request.user.is_superuser:
            edit_permissions = 'all'

        return edit_permissions

    def get_allowed_actions(self, request):
        group = list(request.user.groups.values_list('id', flat=True).all())
        current_app = request.resolver_match.func.model_admin.model._meta.app_label
        model_name = request.resolver_match.func.model_admin.model._meta.object_name

        actions = list(
            ManagementActions.objects.filter(fieldlist__management__group__in=group, fieldlist__model=model_name,
                                             fieldlist__management__application=current_app).values_list(
                'title', 'description'))

        return actions

    # Control what field to show in an admin page inline
    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            if not request.user.is_superuser:
                # hide MyInline in the add view
                allowed_fields = self.get_allowed_permissions(request, inline.model._meta.object_name)
                field_sets = []
                model_fields = [item.name for item in inline.model._meta.get_fields() if
                                not item.auto_created and item.concrete and item.editable]

                if not inline.fields:
                    inline.fields = []

                for permit in model_fields:
                    if permit in allowed_fields and permit in inline.fields:
                        field_sets.append(permit)

                if inline.exclude:
                    for f in inline.exclude:
                        if f in field_sets:
                            field_sets.remove(f)
                inline.fields = field_sets
            yield inline.get_formset(request, obj), inline

    # Handling save procedure for management deactivated fields
    def save_formset(self, request, form, formset, change):

        if not request.user.is_superuser:
            for inline in self.get_inline_instances(request):
                instances = formset.save(commit=False)
                group = list(request.user.groups.values_list('id', flat=True).all())
                current_app = request.resolver_match.func.model_admin.model._meta.app_label
                model_name = formset.model._meta.object_name

                allowed_fields = self.get_allowed_permissions(request, inline.model._meta.object_name)
                field_sets = []
                model_fields = [item.name for item in inline.model._meta.get_fields() if
                                not item.auto_created and item.concrete and item.editable]

                for permit in model_fields:
                    if permit not in allowed_fields:
                        field_sets.append(permit)
                try:
                    for instance in instances:
                        for field in field_sets:
                            default = FieldList.objects.filter(name=field, management__group__in=group,
                                                               model=model_name,
                                                               management__application=current_app).values_list(
                                'default',
                                flat=True).first()
                            if default:
                                try:
                                    # Check if it is a foreign key
                                    getattr(instance, field + '_id')
                                    field_obj = instance._meta.get_field(field).remote_field.model.objects.filter(
                                        id=default).first()
                                    # Entered default value is not correct
                                    if not field_obj:
                                        raise ValueError(
                                            '{' + str(field) + " default value not found for foreign key" + '}')

                                    # Save default value
                                    setattr(instance, field + '_id', field_obj.id)
                                    instance.save()
                                except:
                                    # it is not a related field so reaplace it as text
                                    setattr(instance, field, default)
                                    instance.save()
                except:
                    raise ValueError('{' + str(field) + " default value not found" + '}')

        return super(BaseModelAdmin, self).save_formset(request, form, formset, change)

    def save_model(self, request, obj, form, change):
        group = list(request.user.groups.values_list('id', flat=True).all())
        current_app = request.resolver_match.func.model_admin.model._meta.app_label
        model_name = request.resolver_match.func.model_admin.model._meta.object_name

        request_object = apps.get_model(current_app, model_name)

        allowed_fields = self.get_fieldsets(request)[0][1]['fields']
        obj.allowed_permissions = self.get_allowed_permissions(request)

        if not request.user.is_superuser:

            # model_fields = [x.name for x in request_object._meta.get_fields(
            #     include_parents=True) if
            #                 hasattr(x,
            #                         'blank') and x.blank == False and 'ptr' not in x.name and 'ctype' not in x.name and x.default]

            model_fields = []

            for x in request_object._meta.get_fields(include_parents=True):
                attr_value = False
                try:
                    attr_value = True if getattr(obj, x.name) else False
                except:
                    attr_value = False

                if hasattr(x, 'blank') and \
                        x.blank == False and \
                        'ptr' not in x.name and \
                        'ctype' not in x.name and \
                        x.default and \
                        not attr_value:
                    model_fields.append(x.name)

            request_object = obj
            filtered_fields = [field for field in model_fields if field not in allowed_fields]

            for field in filtered_fields:

                ##Enable this line to fetch expected value from field's own table in django model
                # default = request.resolver_match.func.model_admin.model._meta.model.objects.filter().values_list(field,flat=True).first()

                # Checking field kind
                is_fk = request.resolver_match.func.model_admin.model._meta.get_field(field).is_relation
                m2m = request.resolver_match.func.model_admin.model._meta.get_field(field).many_to_many
                one2one = request.resolver_match.func.model_admin.model._meta.get_field(field).one_to_one
                field_type = request.resolver_match.func.model_admin.model._meta.get_field(field).get_internal_type()

                default = FieldList.objects.filter(name=field, management__group__in=group, model=model_name,
                                                   management__application=current_app).values_list('default',
                                                                                                    flat=True).first()

                try:
                    if (one2one or is_fk or m2m):
                        field_obj = (request_object._meta.get_field(field)).remote_field.model.objects.filter(
                            id=default).first()
                        if default:
                            setattr(request_object, (field + '_id'), field_obj.id)

                    elif field_type not in ['AutoField']:
                        setattr(request_object, field, default)

                    obj = request_object

                except:
                    raise ValueError('{' + str(field) + " default value not found" + '}')

        super(BaseModelAdmin, self).save_model(request, obj, form, change)
