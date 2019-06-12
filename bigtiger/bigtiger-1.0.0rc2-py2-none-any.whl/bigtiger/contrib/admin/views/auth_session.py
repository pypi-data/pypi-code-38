# -*- coding: utf-8 -*-

"""
用户管理|会话信息
Created on 2017-07-19
@author: linkeddt.com
"""

from bigtiger.views.decorators import jsonresponse, excelresponse
from bigtiger.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView)

from django_sae.models.session import SessionModel as AuthSessionModel

from bigtiger.contrib.admin.forms.auth_session import (
    AuthSessionSearchForm, AuthSessionEditForm, AuthSessionEditFormAdmin)


class AuthSessionListView(ListView):
    template_name = "admin/pages/auth_session/table.htm"
    search_form_class = AuthSessionSearchForm
    search_form_initial = {'sort': 'expire_date', 'order': 'desc'}

    def search(self):
        if self.search_form.is_valid():
            cd = self.search_form.cleaned_data

            service = AuthSessionModel()
            page = service.get_page_query(
                self.page_limit, self.page_offset, cd['sort'], cd['order'])
            return page['data'], page['count']

    @jsonresponse()
    def json(self):
        result, total = self.search()
        return {'data': result, "message": None, "pages": self.page_index, "success": True, "total": total}


class AuthSessionDeleteView(DeleteView):

    def get_mime_type(self):
        return self.kwargs.get(self.mime_type_kwarg, None)

    def delete(self, pk, pks):
        service = AuthSessionModel()
        service.tran_delete(pks)

    def clear_expired(self, pk, pks):
        service = AuthSessionModel()
        service.clear_expired()


class AuthSessionDetailView(DetailView):
    template_name = "admin/pages/auth_session/detail.htm"

    def search(self, pk, pks):
        service = AuthSessionModel()
        d = service.get_one(pk)
        return d
