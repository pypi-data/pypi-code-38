# -*- coding: utf-8 -*-

"""
用户管理|权限信息
Created on 2017-07-19
@author: linkeddt.com
"""

from bigtiger.utils.unique import get_uuid
from bigtiger.views.decorators import jsonresponse, excelresponse
from bigtiger.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView)

from bigtiger.contrib.admin.forms.auth_permission import (
    AuthPermissionSearchForm, AuthPermissionEditForm, AuthPermissionCreateForm,
    AuthPermissionEditFormAdmin, AuthPermissionCreateFormAdmin)
from bigtiger.contrib.admin.models.auth_permission import AuthPermissionModel


class AuthPermissionListView(ListView):
    template_name = "admin/pages/auth_permission/table.htm"
    search_form_class = AuthPermissionSearchForm

    def search(self):
        if self.search_form.is_valid():
            cd = self.search_form.cleaned_data
            service = AuthPermissionModel()
            lst = service.get_list_system_tree()
            return lst, len(lst)

    @jsonresponse()
    def json(self):
        result, total = self.search()
        return {'data': result, "message": None, "pages": self.page_index, "success": True, "total": total}


class AuthPermissionTreeView(ListView):

    @jsonresponse(safe=False)
    def json(self):
        service = AuthPermissionModel()
        nodes = service.get_tree_node()
        return nodes


class AuthPermissionAddView(CreateView):
    template_name = "admin/pages/auth_permission/edit.htm"
    form_class = AuthPermissionCreateForm
    form_admin_class = AuthPermissionCreateFormAdmin

    def fill_request_data(self):
        return {'id': get_uuid()}

    def add(self, cd):
        parent_id = cd['parent_id']
        del cd['_id'], cd['parent_id'], cd['_new_parent_id']

        service = AuthPermissionModel()
        service.tran_add(cd, parent_id)


class AuthPermissionEditView(UpdateView):
    template_name = "admin/pages/auth_permission/edit.htm"
    form_class = AuthPermissionEditForm
    form_admin_class = AuthPermissionEditFormAdmin

    def get_init_form_data(self, pk, pks):
        service = AuthPermissionModel()
        d = service.get_detail(pk)
        d['_id'] = d['id']
        d['_new_parent_id'] = d['parent_id']
        return d

    def modify(self, cd):
        _id = cd['_id']
        _new_parent_id = cd['_new_parent_id']
        parent_id = cd['parent_id']

        del cd['_id'], cd['parent_id'], cd['_new_parent_id']

        service = AuthPermissionModel()
        if parent_id == _new_parent_id:
            service.modify(_id, cd)
        else:
            service.tran_modify(cd, parent_id)


class AuthPermissionDeleteView(DeleteView):

    def delete(self, pk, pks):
        service = AuthPermissionModel()
        service.delete(pk)


class AuthPermissionDetailView(DetailView):
    template_name = "admin/pages/auth_permission/detail.htm"

    def search(self, pk, pks):
        service = AuthPermissionModel()
        d = service.get_detail(pk)
        return d
