# -*- coding:utf-8 -*-
from collections import OrderedDict
from functools import partial

from django.contrib.admin.utils import flatten_fieldsets
from django.core.exceptions import FieldError
from django.core.paginator import Paginator
from django.forms import modelform_factory
from django.forms.models import modelform_defines_fields
from django.views.generic import RedirectView

__author__ = 'denishuang'
#
#
# class ApiSet(object):
#     list_display = ('__str__',)
#     list_display_links = ()
#     list_filter = ()
#     list_select_related = False
#     list_per_page = 100
#     list_max_show_all = 200
#     list_editable = ()
#     search_fields = ()
#     date_hierarchy = None
#     save_as = False
#     save_on_top = False
#     paginator = Paginator
#     preserve_filters = True
#     inlines = []
#
#     # Custom templates (designed to be over-ridden in subclasses)
#     add_form_template = None
#     change_form_template = None
#     change_list_template = None
#     delete_confirmation_template = None
#     delete_selected_confirmation_template = None
#     object_history_template = None
#
#     # Actions
#     actions = []
#     actions_on_top = True
#     actions_on_bottom = False
#     actions_selection_counter = True
#
#
#     def __init__(self, model, admin_site):
#         self.model = model
#         self.opts = model._meta
#         self.admin_site = admin_site
#         super(ApiSet, self).__init__()
#
#     def __str__(self):
#         return "%s.%s" % (self.model._meta.app_label, self.__class__.__name__)
#
#     def get_urls(self):
#         from django.conf.urls import url
#
#         def wrap(view):
#             return view
#             # def wrapper(*args, **kwargs):
#             #     return self.admin_site.admin_view(view)(*args, **kwargs)
#             # wrapper.model_admin = self
#             # return update_wrapper(wrapper, view)
#
#         info = self.model._meta.app_label, self.model._meta.model_name
#
#         urlpatterns = [
#             url(r'^$', wrap(self.changelist_view), name='%s_%s_changelist' % info),
#             url(r'^add/$', wrap(self.add_view), name='%s_%s_add' % info),
#             url(r'^(.+)/history/$', wrap(self.history_view), name='%s_%s_history' % info),
#             url(r'^(.+)/delete/$', wrap(self.delete_view), name='%s_%s_delete' % info),
#             url(r'^(.+)/change/$', wrap(self.change_view), name='%s_%s_change' % info),
#             url(r'^(.+)/$', wrap(self.detailview), name='%s_%s_detail' % info),
#         ]
#         return urlpatterns
#
#     def urls(self):
#         return self.get_urls()
#
#     urls = property(urls)
#
#    def get_model_perms(self, request):
#         """
#         Returns a dict of all perms for this model. This dict has the keys
#         ``add``, ``change``, and ``delete`` mapping to the True/False for each
#         of those actions.
#         """
#         return {
#             'add': self.has_add_permission(request),
#             'change': self.has_change_permission(request),
#             'delete': self.has_delete_permission(request),
#         }
#
#     def get_fields(self, request, obj=None):
#         if self.fields:
#             return self.fields
#         form = self.get_form(request, obj, fields=None)
#         return list(form.base_fields) + list(self.get_readonly_fields(request, obj))
#
#     def get_form(self, request, obj=None, **kwargs):
#         """
#         Returns a Form class for use in the admin add view. This is used by
#         add_view and change_view.
#         """
#         if 'fields' in kwargs:
#             fields = kwargs.pop('fields')
#         else:
#             fields = flatten_fieldsets(self.get_fieldsets(request, obj))
#         if self.exclude is None:
#             exclude = []
#         else:
#             exclude = list(self.exclude)
#         readonly_fields = self.get_readonly_fields(request, obj)
#         exclude.extend(readonly_fields)
#         if self.exclude is None and hasattr(self.form, '_meta') and self.form._meta.exclude:
#             # Take the custom ModelForm's Meta.exclude into account only if the
#             # ModelAdmin doesn't define its own.
#             exclude.extend(self.form._meta.exclude)
#         # if exclude is an empty list we pass None to be consistent with the
#         # default on modelform_factory
#         exclude = exclude or None
#
#         # Remove declared form fields which are in readonly_fields.
#         new_attrs = OrderedDict(
#             (f, None) for f in readonly_fields
#             if f in self.form.declared_fields
#         )
#         form = type(self.form.__name__, (self.form,), new_attrs)
#
#         defaults = {
#             "form": form,
#             "fields": fields,
#             "exclude": exclude,
#             "formfield_callback": partial(self.formfield_for_dbfield, request=request),
#         }
#         defaults.update(kwargs)
#
#         if defaults['fields'] is None and not modelform_defines_fields(defaults['form']):
#             defaults['fields'] = forms.ALL_FIELDS
#
#         try:
#             return modelform_factory(self.model, **defaults)
#         except FieldError as e:
#             raise FieldError('%s. Check fields/fieldsets/exclude attributes of class %s.'
#                              % (e, self.__class__.__name__))
