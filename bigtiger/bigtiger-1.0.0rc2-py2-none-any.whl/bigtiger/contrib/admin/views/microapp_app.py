# -*- coding: utf-8 -*-

"""
微应用|应用信息
Created on 2017-07-19
@author: linkeddt.com
"""

from bigtiger.views.decorators import jsonresponse, excelresponse
from bigtiger.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView)
from bigtiger.utils.unique import get_uuid

from bigtiger.contrib.admin.forms.microapp_app import (
    MicroappAppSearchForm, MicroappAppEditForm, MicroappAppEditFormAdmin)
from bigtiger.contrib.admin.models.microapp_app import MicroappAppModel


class MicroappAppListView(ListView):
    template_name = "admin/pages/microapp_app/table.htm"
    search_form_class = MicroappAppSearchForm
    search_form_initial = {'app_name': '', 'sort': 'app_code', 'order': 'asc'}

    def search(self):
        if self.search_form.is_valid():
            cd = self.search_form.cleaned_data

            service = MicroappAppModel()
            lst, count = service.get_page_query(
                cd['app_name'], self.page_limit, self.page_offset, cd['sort'], cd['order'])
            return lst, count

    @jsonresponse()
    def json(self):
        result, total = self.search()
        return {'data': result, "message": None, "pages": self.page_index, "success": True, "total": total}


class MicroappAppAddView(CreateView):
    template_name = "admin/pages/microapp_app/edit.htm"
    form_class = MicroappAppEditForm
    form_admin_class = MicroappAppEditFormAdmin

    def fill_request_data(self):
        return {'id': get_uuid()}

    def add(self, cd):
        del cd['_id']
        service = MicroappAppModel()
        service.add(cd)


class MicroappAppEditView(UpdateView):
    template_name = "admin/pages/microapp_app/edit.htm"
    form_class = MicroappAppEditForm
    form_admin_class = MicroappAppEditFormAdmin

    def get_init_form_data(self, pk, pks):
        service = MicroappAppModel()
        d = service.get_detail(pk)
        d['_id'] = d['id']
        return d

    def modify(self, cd):
        _id = cd['_id']
        del cd['_id']

        service = MicroappAppModel()
        service.modify(_id, cd)


class MicroappAppDeleteView(DeleteView):

    def delete(self, pk, pks):
        service = MicroappAppModel()
        service.delete(pk)


class MicroappAppDetailView(DetailView):
    template_name = "admin/pages/microapp_app/detail.htm"

    def search(self, pk, pks):
        service = MicroappAppModel()
        d = service.get_detail(pk)
        return d
