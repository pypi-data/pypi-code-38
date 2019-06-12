# -*- coding: utf-8 -*-

"""
系统更新日志
Created on 2017-07-19
@author: linkeddt.com
"""

from bigtiger.views.decorators import jsonresponse, excelresponse
from bigtiger.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView)
from bigtiger.utils.unique import get_uuid

from bigtiger.contrib.admin.forms.sys_update_log import (
    SysUpdateLogSearchForm, SysUpdateLogEditForm, SysUpdateLogEditFormAdmin)
from bigtiger.contrib.admin.models.sys_update_log import SysUpdateLogModel


class SysUpdateLogListView(ListView):
    template_name = "admin/pages/sys_update_log/table.htm"
    search_form_class = SysUpdateLogSearchForm
    search_form_initial = {'sort': 'version_number', 'order': 'desc'}

    def search(self):
        if self.search_form.is_valid():
            cd = self.search_form.cleaned_data

            service = SysUpdateLogModel()
            lst, count = service.get_page_query(
                self.page_limit, self.page_offset, cd['sort'], cd['order'])
            return lst, count

    @excelresponse(u'系统更新日志', 'sys_update_log.xls', 2, 0)
    def excel(self):
        result, _ = self.search()
        if result:
            return [(item['version_number'], item['public_date'], item['update_content'], item['remark'], ) for item in result]
        return None

    @jsonresponse()
    def json(self):
        result, total = self.search()
        return {'data': result, "message": None, "pages": self.page_index, "success": True, "total": total}


class SysUpdateLogAddView(CreateView):
    template_name = "admin/pages/sys_update_log/edit.htm"
    form_class = SysUpdateLogEditForm
    form_admin_class = SysUpdateLogEditFormAdmin

    def add(self, cd):
        del cd['_id']
        service = SysUpdateLogModel()
        service.add(cd)


class SysUpdateLogEditView(UpdateView):
    template_name = "admin/pages/sys_update_log/edit.htm"
    form_class = SysUpdateLogEditForm
    form_admin_class = SysUpdateLogEditFormAdmin

    def get_init_form_data(self, pk, pks):
        service = SysUpdateLogModel()
        d = service.get_detail(pk)
        d['_id'] = d['version_number']
        return d

    def modify(self, cd):
        _id = cd['_id']
        del cd['_id']

        service = SysUpdateLogModel()
        service.modify(_id, cd)


class SysUpdateLogDeleteView(DeleteView):

    def delete(self, pk, pks):
        service = SysUpdateLogModel()
        service.tran_delete(pks)


class SysUpdateLogDetailView(DetailView):
    template_name = "admin/pages/sys_update_log/detail.htm"

    def search(self, pk, pks):
        service = SysUpdateLogModel()
        d = service.get_detail(pk)
        return d
