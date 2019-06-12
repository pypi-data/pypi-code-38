# -*- coding: utf-8 -*-

"""
微应用|会话票据
Created on 2017-07-19
@author: linkeddt.com
"""

from bigtiger.views.decorators import jsonresponse, excelresponse
from bigtiger.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView)
from bigtiger.utils.unique import get_uuid

from bigtiger.contrib.admin.forms.microapp_token import (
    MicroappTokenSearchForm, MicroappTokenEditForm, MicroappTokenEditFormAdmin)
from bigtiger.contrib.admin.models.microapp_token import MicroappTokenModel


class MicroappTokenListView(ListView):
    template_name = "admin/pages/microapp_token/table.htm"
    search_form_class = MicroappTokenSearchForm
    search_form_initial = {'app_name': '',
                           'sort': 'expire_date', 'order': 'desc'}

    def search(self):
        if self.search_form.is_valid():
            cd = self.search_form.cleaned_data

            service = MicroappTokenModel()
            lst, count = service.get_page_query(
                cd['app_name'], self.page_limit, self.page_offset, cd['sort'], cd['order'])
            return lst, count

    @jsonresponse()
    def json(self):
        result, total = self.search()
        return {'data': result, "message": None, "pages": self.page_index, "success": True, "total": total}


class MicroappTokenAddView(CreateView):
    template_name = "admin/pages/microapp_token/edit.htm"
    form_class = MicroappTokenEditForm
    form_admin_class = MicroappTokenEditFormAdmin

    def fill_request_data(self):
        return {'id': get_uuid()}

    def add(self, cd):
        del cd['_id']

        service = MicroappTokenModel()
        service.add(cd)


class MicroappTokenEditView(UpdateView):
    template_name = "admin/pages/microapp_token/edit.htm"
    form_class = MicroappTokenEditForm
    form_admin_class = MicroappTokenEditFormAdmin

    def get_init_form_data(self, pk, pks):
        service = MicroappTokenModel()
        d = service.get_detail(pk)
        d['_id'] = d['id']
        return d

    def modify(self, cd):
        _id = cd['_id']
        del cd['_id']

        service = MicroappTokenModel()
        service.modify(_id, cd)


class MicroappTokenDeleteView(DeleteView):

    def delete(self, pk, pks):
        service = MicroappTokenModel()
        service.tran_delete(pks)


class MicroappTokenDetailView(DetailView):
    template_name = "admin/pages/microapp_token/detail.htm"

    def search(self, pk, pks):
        service = MicroappTokenModel()
        d = service.get_detail(pk)
        return d
