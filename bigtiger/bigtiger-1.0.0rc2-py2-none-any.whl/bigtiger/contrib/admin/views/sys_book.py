# -*- coding: utf-8 -*-

"""
系统数据字典
Created on 2017-07-19
@author: linkeddt.com
"""

from bigtiger.views.decorators import jsonresponse, excelresponse
from bigtiger.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView)
from bigtiger.utils.unique import get_uuid

from bigtiger.contrib.admin.forms.sys_book import (
    SysBookSearchForm, SysBookEditForm, SysBookEditFormAdmin)
from bigtiger.contrib.admin.models.sys_book import SysBookModel


class SysBookListView(ListView):
    template_name = "admin/pages/sys_book/table.htm"
    search_form_class = SysBookSearchForm
    search_form_initial = {'sort': 'class_code', 'order': 'asc'}

    def search(self):
        if self.search_form.is_valid():
            cd = self.search_form.cleaned_data

            service = SysBookModel()
            lst, count = service.get_page_query(
                cd['class_code'], cd['code'], cd['text'], cd['remark'], self.page_limit, self.page_offset, cd['sort'], cd['order'])
            return lst, count

    @excelresponse(u'系统数据字典', 'sys_book.xls', 2, 0)
    def excel(self):
        result, _ = self.search()
        if result:
            return [(item['id'], item['class_code'], item['code'], item['text'], item['order_number'], item['is_enable'], item['remark'], ) for item in result]
        return None

    @jsonresponse()
    def json(self):
        result, total = self.search()
        return {'data': result, "message": None, "pages": self.page_index, "success": True, "total": total}


class SysBookAddView(CreateView):
    template_name = "admin/pages/sys_book/edit.htm"
    form_class = SysBookEditForm
    form_admin_class = SysBookEditFormAdmin

    def add(self, cd):
        del cd['_id']

        cd['id'] = get_uuid()
        service = SysBookModel()
        service.add(cd)


class SysBookEditView(UpdateView):
    template_name = "admin/pages/sys_book/edit.htm"
    form_class = SysBookEditForm
    form_admin_class = SysBookEditFormAdmin

    def get_init_form_data(self, pk, pks):
        service = SysBookModel()
        d = service.get_detail(pk)
        d['_id'] = d['id']
        return d

    def modify(self, cd):
        _id = cd['_id']
        del cd['_id']

        service = SysBookModel()
        service.modify(_id, cd)


class SysBookDeleteView(DeleteView):

    def delete(self, pk, pks):
        service = SysBookModel()
        service.tran_delete(pks)


class SysBookDetailView(DetailView):
    template_name = "admin/pages/sys_book/detail.htm"

    def search(self, pk, pks):
        service = SysBookModel()
        d = service.get_detail(pk)
        return d
