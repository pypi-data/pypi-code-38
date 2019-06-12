# -*- coding: utf-8 -*-

"""
用户管理|组信息
Created on 2017-07-19
@author: linkeddt.com
"""

from bigtiger.views.decorators import jsonresponse, excelresponse
from bigtiger.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView)
from bigtiger.utils.unique import get_uuid

from bigtiger.contrib.admin.forms.auth_group import (
    AuthGroupSearchForm, AuthGroupEditForm, AuthGroupEditFormAdmin)
from bigtiger.contrib.admin.models.auth_group import AuthGroupModel
from bigtiger.contrib.admin.models.auth_group_permissions import AuthGroupPermissionsModel


class AuthGroupListView(ListView):
    template_name = "admin/pages/auth_group/table.htm"
    search_form_class = AuthGroupSearchForm
    search_form_initial = {'sort': 'name', 'order': 'asc'}

    def search(self):
        if self.search_form.is_valid():
            cd = self.search_form.cleaned_data

            service = AuthGroupModel()
            lst, count = service.get_page_query(
                cd['group_name'], self.page_limit, self.page_offset, cd['sort'], cd['order'])
            return lst, count

    @excelresponse(u'用户管理|组信息', 'auth_group.xls', 2, 0)
    def excel(self):
        result, _ = self.search()
        if result:
            return [(item['id'], item['name'], item['type'], item['remark'], ) for item in result]
        return None

    @jsonresponse()
    def json(self):
        result, total = self.search()
        return {'data': result, "message": None, "pages": self.page_index, "success": True, "total": total}


class AuthGroupAddView(CreateView):
    """ 用户管理|组信息新增
    """
    template_name = "admin/pages/auth_group/edit.htm"
    form_class = AuthGroupEditForm
    form_admin_class = AuthGroupEditFormAdmin

    def add(self, cd):
        permissions = cd['permissions']

        group_id = get_uuid()
        cd['id'] = group_id

        arr = permissions.split(',')
        group_permissions = []
        for item in arr:
            group_permissions.append(
                {'id': get_uuid(), 'group_id': group_id,  'permission_id': item})

        del cd['_id'], cd['permissions']

        service = AuthGroupModel()
        service.tran_add(cd, group_permissions)


class AuthGroupEditView(UpdateView):
    template_name = "admin/pages/auth_group/edit.htm"
    form_class = AuthGroupEditForm
    form_admin_class = AuthGroupEditFormAdmin

    def get_init_form_data(self, pk, pks):
        service = AuthGroupModel()
        d = service.get_one(pk)
        d['_id'] = d['id']

        service = AuthGroupPermissionsModel()
        lst = service.get_list_group_id(d['id'])
        permissions = [item['permission_id'] for item in lst]
        d['permissions'] = ','.join(permissions)
        return d

    def modify(self, cd):
        _id = cd['_id']
        permissions = cd['permissions']

        arr = permissions.split(',')
        group_permissions = []
        for item in arr:
            group_permissions.append(
                {'id': get_uuid(), 'group_id': _id,  'permission_id': item})

        del cd['_id'], cd['permissions']

        service = AuthGroupModel()
        service.tran_modify(_id, cd, group_permissions)


class AuthGroupDeleteView(DeleteView):

    def delete(self, pk, pks):
        service = AuthGroupModel()
        service.tran_delete(pks)


class AuthGroupDetailView(DetailView):
    template_name = "admin/pages/auth_group/detail.htm"

    def search(self, pk, pks):
        service = AuthGroupModel()
        d = service.get_detail(pk)
        return d
