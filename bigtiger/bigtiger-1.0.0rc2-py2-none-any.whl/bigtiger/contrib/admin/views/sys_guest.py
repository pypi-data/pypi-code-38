# -*- coding: utf-8 -*-

"""
系统访客
Created on 2017-07-19
@author: linkeddt.com
"""

from bigtiger.views.decorators import jsonresponse, excelresponse
from bigtiger.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView)
from bigtiger.utils.unique import get_uuid

from bigtiger.contrib.admin.forms.sys_guest import (
    SysGuestSearchForm, SysGuestEditForm, SysGuestEditFormAdmin)
from bigtiger.contrib.admin.models.sys_guest import SysGuestModel


class SysGuestListView(ListView):
    template_name = "admin/pages/sys_guest/table.htm"
    search_form_class = SysGuestSearchForm
    search_form_initial = {'sort': 'request_date', 'order': 'desc'}

    def search(self):
        if self.search_form.is_valid():
            cd = self.search_form.cleaned_data
            begin_date, end_date = cd['daterange']

            service = SysGuestModel()
            lst, count = service.get_page_query(
                begin_date, end_date, cd['location'], self.page_limit, self.page_offset, cd['sort'], cd['order'])
            return lst, count

    @excelresponse(u'系统访客', 'sys_guest.xls', 2, 0)
    def excel(self):
        result, _ = self.search()
        if result:
            return [(item['id'], item['ip'], item['request_date'], item['location'], item['remark'], ) for item in result]
        return None

    @jsonresponse()
    def json(self):
        result, total = self.search()
        return {'data': result, "message": None, "pages": self.page_index, "success": True, "total": total}


class SysGuestAddView(CreateView):
    template_name = "admin/pages/sys_guest/edit.htm"
    form_class = SysGuestEditForm
    form_admin_class = SysGuestEditFormAdmin

    def add(self, cd):
        del cd['_id']

        service = SysGuestModel()
        service.add(cd)


class SysGuestEditView(UpdateView):
    template_name = "admin/pages/sys_guest/edit.htm"
    form_class = SysGuestEditForm
    form_admin_class = SysGuestEditFormAdmin

    def get_init_form_data(self, pk, pks):
        service = SysGuestModel()
        d = service.get_detail(pk)
        d['_id'] = d['id']
        return d

    def modify(self, cd):
        _id = cd['_id']
        del cd['_id']

        service = SysGuestModel()
        service.modify(_id, cd)


class SysGuestDeleteView(DeleteView):

    def delete(self, pk, pks):
        service = SysGuestModel()
        service.tran_delete(pks)


class SysGuestDetailView(DetailView):
    template_name = "admin/pages/sys_guest/detail.htm"

    def search(self, pk, pks):
        service = SysGuestModel()
        d = service.get_detail(pk)
        return d
