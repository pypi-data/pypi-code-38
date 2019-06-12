# -*- coding: utf-8 -*-

'''
Created on 2017-6-22
@author: linkeddt.com
'''

from __future__ import unicode_literals, print_function

from django.conf import settings
from django.views.generic.base import TemplateResponseMixin, ContextMixin, View

from bigtiger.views.generic.base import PermissionMixin, permission


class MultipleObjectMixin(ContextMixin):
    search_form_class = None
    search_form_initial = {}

    mime_type_kwarg = 'MIME_TYPE'
    page_index_kwarg = 'page'
    page_size_kwarg = 'rows'
    order_kwarg = 'order'
    sort_kwarg = 'sort'

    def get_objects(self):
        mime_type = self.kwargs.get(self.mime_type_kwarg, None)
        if mime_type == 'json':
            obj = self.json()
        elif mime_type == 'excel':
            obj = self.excel()
        else:
            if self.search_form_class:
                self.search_form = self.init_form(self.request)
        return obj

    def get_search_form_initial(self):
        return self.search_form_initial.copy()

    def get_json_response(self):
        return self.json()

    def get_excel_response(self):
        return self.excel()

    def init_search_form(self):
        if self.search_form_class:
            query = self.request.GET.copy()
            if hasattr(self, 'set_request_query'):
                self.set_request_query(query)
            initial = self.get_search_form_initial()
            if initial and isinstance(initial, dict):
                for k, v in initial.iteritems():
                    if k not in query:
                        query[k] = v
            self.search_form = self.search_form_class(query, r=self.request)
        else:
            self.search_form = None

    def get_mime_type(self):
        return self.kwargs.get(self.mime_type_kwarg, None)

    def get_context_data(self, **kwargs):
        context = {}
        context.update(kwargs)
        return super(MultipleObjectMixin, self).get_context_data(**context)

    @property
    def page_index(self):
        """获取分页显示第几页"""
        return int(self.request.GET.get(self.page_index_kwarg, 1))

    @property
    def page_size(self):
        """获取分页每页显示的记录条数"""
        page_size = self.request.GET.get(self.page_size_kwarg, None)
        if page_size:
            return int(page_size)

        if hasattr(settings, 'EXPORT_PAGESIZE'):
            return int(settings.EXPORT_PAGESIZE)
        return 1000

    @property
    def page_limit(self):
        return self.page_size

    @property
    def page_offset(self):
        return (self.page_index - 1) * self.page_size


class BaseListView(MultipleObjectMixin, PermissionMixin, View):
    """
    A base view for displaying a list of objects.
    """

    @permission
    def get(self, request, *args, **kwargs):
        mime_type = self.get_mime_type()

        self.init_search_form()
        if mime_type == 'json':
            return self.get_json_response()
        if mime_type == 'excel':
            return self.get_excel_response()

        self.permission = self.get_url_permission()
        kwargs.update(permission=self.permission, form=self.search_form)
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class MultipleObjectTemplateResponseMixin(TemplateResponseMixin):
    template_extend_names = None
    template_extend_dynamic = False

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response, using the `response_class` for this
        view, with a template rendered with the given context.

        If any keyword arguments are provided, they will be
        passed to the constructor of the response class.
        """
        if self.template_extend_dynamic:
            extend_name = self.request.GET.get('_extend', 'default')
            extends = self.get_template_extend_names()
            context.update({'d_extend': extends.get(extend_name, None)})

        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            **response_kwargs
        )

    def get_template_extend_names(self):
        if self.template_extend_names is None:
            raise ImproperlyConfigured(
                "TemplateResponseMixin requires either a definition of "
                "'template_extend_names' or an implementation of 'get_template_extend_names()'")
        else:
            return self.template_extend_names


class ListView(MultipleObjectTemplateResponseMixin, BaseListView):
    """
    Render some list of objects, set by `self.model` or `self.queryset`.
    `self.queryset` can actually be any iterable of items, not just a queryset.
    """
