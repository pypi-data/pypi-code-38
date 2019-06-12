# -*- coding: utf-8 -*-

from datetime import datetime

from django_restful import RestfulApiError
from bigtiger.core.exceptions import SuspiciousOperation

from bigtiger.views.decorators import jsonresponse, excelresponse
from bigtiger.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView)
from bigtiger.utils.unique import get_uuid

from bigtiger.contrib.admin.forms.auth_user import (AuthUserSearchForm, AuthUserCreateForm, AuthUserEditForm,
                                                    AuthUserCreateFormAdmin, AuthUserEditFormAdmin,
                                                    AuthUserModifyPwdForm, AuthUserModifyPwdFormAdmin, role_manager)

from bigtiger.contrib.admin.models.auth_user import AuthUserModel
from django_sae.models.user import UserModel


class AuthUserListView(ListView):
    template_name = "admin/pages/auth_user/table.htm"
    search_form_class = AuthUserSearchForm
    search_form_initial = {'roles': '*', 'sort': 'user_name', 'order': 'asc'}

    def search(self):
        if self.search_form.is_valid():
            cd = self.search_form.cleaned_data

            service = AuthUserModel()
            lst, count = service.get_page_query(
                cd['roles'], cd['user_name'], self.page_limit, self.page_offset, cd['sort'], cd['order'])

            role = role_manager()
            if lst:
                for item in lst:
                    item['roles_name'] = role(item['roles'])

            return lst, count

    @excelresponse(u'用户管理|用户基本信息', 'auth_user.xls', 2, 0)
    def excel(self):
        result, _ = self.search()
        if result:
            return [(item['id'], item['ad_code'], item['login_name'], item['login_password'], item['first_name'], item['last_name'], item['user_name'], item['sex'], item['phone_number'], item['email'], item['is_active'], item['is_superuser'], item['is_dba'], item['is_read'], item['is_leader'], item['roles'], item['domain'], item['create_date'], item['last_login_date'], item['last_login_ip'], item['wechat_json'], item['extend_json'], item['remark'], ) for item in result]
        return None

    @jsonresponse()
    def json(self):
        result, total = self.search()
        return {'data': result, "message": None, "pages": self.page_index, "success": True, "total": total}


class AuthUserAddView(CreateView):
    template_name = "admin/pages/auth_user/edit.htm"
    form_class = AuthUserCreateForm
    form_admin_class = AuthUserCreateFormAdmin

    def fill_request_data(self):
        return {'id': get_uuid()}

    def add(self, cd):
        del cd['_id']

        cd['user_name'] = '{}{}'.format(cd['first_name'], cd['last_name'])
        cd['is_superuser'] = 0
        cd['create_date'] = datetime.now()
        cd['last_login_date'] = None
        cd['last_login_ip'] = None
        cd['wechat_json'] = ''
        cd['extend_json'] = ''
        cd['roles'] = ','.join(cd['roles'])

        service = AuthUserModel()
        service.add(cd)


class AuthUserEditView(UpdateView):
    template_name = "admin/pages/auth_user/edit.htm"
    form_class = AuthUserEditForm
    form_admin_class = AuthUserEditFormAdmin

    def get_init_form_data(self, pk, pks):
        service = AuthUserModel()
        d = service.get_detail(pk)
        d['_id'] = d['id']
        d['roles'] = d['roles'].split(',')
        return d

    def modify(self, cd):
        _id = cd['_id']
        del cd['_id']

        cd['user_name'] = '{}{}'.format(cd['first_name'], cd['last_name'])
        cd['is_superuser'] = 0
        cd['create_date'] = datetime.now()
        cd['last_login_date'] = None
        cd['last_login_ip'] = None
        cd['extend_json'] = ''
        cd['roles'] = ','.join(cd['roles'])

        service = AuthUserModel()
        service.modify(_id, cd)


class AuthUserDeleteView(DeleteView):

    def delete(self, pk, pks):
        service = AuthUserModel()
        service.tran_delete(pks)


class AuthUserDetailView(DetailView):
    template_name = "admin/pages/auth_user/detail.htm"

    def search(self, pk, pks):
        service = AuthUserModel()
        d = service.get_detail(pk)
        role = role_manager()
        d['roles_name'] = role(d['roles'])
        return d
