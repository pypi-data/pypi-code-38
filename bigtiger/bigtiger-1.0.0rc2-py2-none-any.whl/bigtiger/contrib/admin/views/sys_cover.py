# -*- coding: utf-8 -*-

"""
系统封面
Created on 2017-07-19
@author: linkeddt.com
"""

import os
import json
from datetime import datetime as dt

from django_store.store import MinioStore

from bigtiger.views.decorators import jsonresponse, excelresponse
from bigtiger.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView)
from bigtiger.utils.unique import get_uuid

from bigtiger.contrib.admin.forms.sys_cover import (
    SysCoverSearchForm, SysCoverEditForm, SysCoverEditFormAdmin)
from bigtiger.contrib.admin.models.sys_cover import SysCoverModel


class SysCoverListView(ListView):
    template_name = "admin/pages/sys_cover/table.htm"
    search_form_class = SysCoverSearchForm
    search_form_initial = {'sort': 'order_number', 'order': 'asc'}

    def search(self):
        if self.search_form.is_valid():
            cd = self.search_form.cleaned_data

            service = SysCoverModel()
            lst, count = service.get_page_query(
                cd['cover_title'], self.page_limit, self.page_offset, cd['sort'], cd['order'])
            return lst, count

    @excelresponse(u'系统封面', 'sys_cover.xls', 2, 0)
    def excel(self):
        result, _ = self.search()
        if result:
            return [(item['id'], item['cover_title'], item['cover_summary'], item['cover_image'], item['cover_thumbnail'], item['upload_date'], item['upload_user'], item['order_number'], item['remark'], ) for item in result]
        return None

    @jsonresponse()
    def json(self):
        result, total = self.search()
        return {'data': result, "message": None, "pages": self.page_index, "success": True, "total": total}


class SysCoverAddView(CreateView):
    template_name = "admin/pages/sys_cover/edit.htm"
    form_class = SysCoverEditForm
    form_admin_class = SysCoverEditFormAdmin

    def add(self, cd):
        del cd['_id']
        cd['id'] = get_uuid()

        uf = self.request.FILES['cover_image_file']
        file_name = uf.name
        _name, ext = os.path.splitext(file_name)
        ext = ext.lower()
        alias_name = '{}{}'.format(cd['id'], ext)

        cd['remark'] = alias_name
        cd['cover_image'] = file_name
        cd['upload_date'] = dt.now()

        ms = MinioStore()
        ms.put_file(uf, alias_name)

        service = SysCoverModel()
        service.add(cd)


class SysCoverEditView(UpdateView):
    template_name = "admin/pages/sys_cover/edit.htm"
    form_class = SysCoverEditForm
    form_admin_class = SysCoverEditFormAdmin

    def get_init_form_data(self, pk, pks):
        service = SysCoverModel()
        d = service.get_detail(pk)
        d['_id'] = d['id']

        cover_image = json.dumps(
            {'flag': "edit", "filename": d['cover_image']})
        d.update({'cover_image': cover_image})
        return d

    def modify(self, cd):
        _id = cd['_id']
        del cd['_id']

        uf = self.request.FILES.get('cover_image_file', None)
        if uf:
            file_name = uf.name
            _name, ext = os.path.splitext(file_name)
            ext = ext.lower()
            alias_name = '{}{}'.format(cd['id'], ext)

            cd['remark'] = alias_name
            cd['cover_image'] = file_name

            mc = MinioStore()
            mc.put_file(uf, alias_name)
        else:
            cd['cover_image'] = json.loads(cd['cover_image'])['filename']
        cd['upload_date'] = dt.now()

        service = SysCoverModel()
        service.modify(_id, cd)


class SysCoverDeleteView(DeleteView):

    def delete(self, pk, pks):
        service = SysCoverModel()
        service.tran_delete(pks)


class SysCoverDetailView(DetailView):
    template_name = "admin/pages/sys_cover/detail.htm"

    def search(self, pk, pks):
        service = SysCoverModel()
        d = service.get_detail(pk)
        return d
