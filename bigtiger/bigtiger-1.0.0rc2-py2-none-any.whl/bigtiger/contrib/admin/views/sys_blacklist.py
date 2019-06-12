# -*- coding: utf-8 -*-

"""
系统黑名单
Created on 2017-07-19
@author: linkeddt.com
"""

from bigtiger.views.decorators import jsonresponse, excelresponse
from bigtiger.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView)
from bigtiger.utils.unique import get_uuid

from bigtiger.contrib.admin.forms.sys_blacklist import (
    SysBlacklistSearchForm, SysBlacklistEditForm, SysBlacklistEditFormAdmin)
from bigtiger.contrib.admin.models.sys_blacklist import SysBlacklistModel


class SysBlacklistListView(ListView):
    template_name = "admin/pages/sys_blacklist/table.htm"
    search_form_class = SysBlacklistSearchForm
    search_form_initial = {'sort': 'end_date', 'order': 'desc'}

    def search(self):
        if self.search_form.is_valid():
            cd = self.search_form.cleaned_data

            service = SysBlacklistModel()
            lst, count = service.get_page_query(
                self.page_limit, self.page_offset, cd['sort'], cd['order'])
            return lst, count

    @excelresponse(u'系统黑名单', 'sys_blacklist.xls', 2, 0)
    def excel(self):
        result, _ = self.search()
        if result:
            return [(item['id'], item['ip'], item['begin_date'], item['end_date'], item['remark'], ) for item in result]
        return None

    @jsonresponse()
    def json(self):
        result, total = self.search()
        return {'data': result, "message": None, "pages": self.page_index, "success": True, "total": total}


class SysBlacklistAddView(CreateView):
    template_name = "admin/pages/sys_blacklist/edit.htm"
    form_class = SysBlacklistEditForm
    form_admin_class = SysBlacklistEditFormAdmin

    def add(self, cd):
        del cd['_id']
        cd['id'] = get_uuid()
        service = SysBlacklistModel()
        service.add(cd)


class SysBlacklistEditView(UpdateView):
    template_name = "admin/pages/sys_blacklist/edit.htm"
    form_class = SysBlacklistEditForm
    form_admin_class = SysBlacklistEditFormAdmin

    def get_init_form_data(self, pk, pks):
        service = SysBlacklistModel()
        d = service.get_detail(pk)
        d['_id'] = d['id']
        return d

    def modify(self, cd):
        _id = cd['_id']
        del cd['_id']

        service = SysBlacklistModel()
        service.modify(_id, cd)


class SysBlacklistDeleteView(DeleteView):

    def delete(self, pk, pks):
        service = SysBlacklistModel()
        service.tran_delete(pks)


class SysBlacklistDetailView(DetailView):
    template_name = "admin/pages/sys_blacklist/detail.htm"

    def search(self, pk, pks):
        service = SysBlacklistModel()
        d = service.get_detail(pk)
        return d
