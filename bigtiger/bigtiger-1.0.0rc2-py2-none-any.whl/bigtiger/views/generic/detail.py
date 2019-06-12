# -*- coding: utf-8 -*-

'''
Created on 2017-6-22
@author: linkeddt.com
'''

from __future__ import unicode_literals, print_function

from django.http import Http404
from django.views.generic.base import TemplateResponseMixin, ContextMixin, View

from bigtiger.views.generic.base import PkContextMixin, PermissionMixin, permission


class SingleObjectMixin(PkContextMixin, ContextMixin):
    pk_split_kwarg = '|'

    def get_object(self):
        key = self.get_key()
        pks = self.get_pks()
        try:
            obj = self.search(key, pks)
        except AttributeError as e:
            raise Http404("%(verbose_name)s 消失在茫茫人海中..." %
                          {'verbose_name': self.pk_split_kwarg.join(pks)})
        return obj

    def get_context_data(self, **kwargs):
        context = {}
        context.update(kwargs)
        return super(SingleObjectMixin, self).get_context_data(**context)


class BaseDetailView(SingleObjectMixin, PermissionMixin, View):
    """
    A base view for displaying a single object
    """

    @permission
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.permission = self.get_url_permission()
        context = self.get_context_data(
            object=self.object, permission=self.permission)
        return self.render_to_response(context)


class SingleObjectTemplateResponseMixin(TemplateResponseMixin):
    pass


class DetailView(SingleObjectTemplateResponseMixin, BaseDetailView):
    """
    Render a "detail" view of an object.

    By default this is a model instance looked up from `self.queryset`, but the
    view will support display of *any* object by overriding `self.get_object()`.
    """
