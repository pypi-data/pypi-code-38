# -*- coding: utf-8 -*-

"""
系统配置
Created on 2017-07-19
@author: linkeddt.com
"""

from bigtiger.views.decorators import jsonresponse, excelresponse
from bigtiger.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView)
from bigtiger.utils.unique import get_uuid

from bigtiger.contrib.admin.forms.sys_config import (
    SysConfigSearchForm, SysConfigEditForm, SysConfigEditFormAdmin)
from bigtiger.contrib.admin.models.sys_config import SysConfigModel


class SysConfigListView(ListView):
    template_name = "admin/pages/sys_config/table.htm"
    search_form_class = SysConfigSearchForm
    search_form_initial = {'config_key': '',
                           'config_name': '', 'sort': 'config_key', 'order': 'asc'}

    def search(self):
        if self.search_form.is_valid():
            cd = self.search_form.cleaned_data

            service = SysConfigModel()
            lst, count = service.get_page_query(
                cd['config_key'], cd['config_name'], self.page_limit, self.page_offset, cd['sort'], cd['order'])
            return lst, count

    @jsonresponse()
    def json(self):
        result, total = self.search()
        return {'data': result, "message": None, "pages": self.page_index, "success": True, "total": total}


class SysConfigAddView(CreateView):
    template_name = "admin/pages/sys_config/edit.htm"
    form_class = SysConfigEditForm
    form_admin_class = SysConfigEditFormAdmin

    def add(self, cd):
        del cd['_id']

        service = SysConfigModel()
        service.add(cd)


class SysConfigEditView(UpdateView):
    template_name = "admin/pages/sys_config/edit.htm"
    form_class = SysConfigEditForm
    form_admin_class = SysConfigEditFormAdmin

    def get_init_form_data(self, pk, pks):
        service = SysConfigModel()
        d = service.get_detail(pk)
        d['_id'] = d['config_key']
        return d

    def modify(self, cd):
        _id = cd['_id']
        del cd['_id']

        service = SysConfigModel()
        service.modify(_id, cd)


class SysConfigDeleteView(DeleteView):

    def delete(self, pk, pks):
        service = SysConfigModel()
        service.tran_delete(pks)


class SysConfigDetailView(DetailView):
    template_name = "admin/pages/sys_config/detail.htm"

    def search(self, pk, pks):
        service = SysConfigModel()
        d = service.get_detail(pk)
        return d
