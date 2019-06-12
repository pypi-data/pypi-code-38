# -*- coding: utf-8 -*-

"""
用户管理|用户日志
Created on 2017-07-19
@author: linkeddt.com
"""

from bigtiger.views.decorators import jsonresponse, excelresponse
from bigtiger.views.generic import ListView, DetailView

from bigtiger.contrib.admin.forms.auth_user_log import AuthUserLogSearchForm
from bigtiger.contrib.admin.models.auth_user_log import AuthUserLogModel

from django_sae.models.user import UserModel


def _get_user():
    service = UserModel()
    users = service.get_all()

    def _get_user_name(user_id):
        lst = [item for item in users if item['id'] == user_id]
        if lst:
            u = lst[0]
            return u.get('user_name', None) or u.get('id', '')
        return ''
    return _get_user_name


class AuthUserLogListView(ListView):
    template_name = "admin/pages/auth_user_log/table.htm"
    search_form_class = AuthUserLogSearchForm
    search_form_initial = {'action_flag': -1, 'daterange_begin': '2017-05-06 16',
                           'status': 0, 'sort': 'action_time', 'order': 'desc'}

    def search(self):
        if self.search_form.is_valid():
            cd = self.search_form.cleaned_data

            begin_date, end_date = cd['daterange']
            service = AuthUserLogModel()
            lst, count = service.get_page_query(
                int(cd['action_flag']), int(cd['status']), begin_date, end_date, cd['action_class'], self.page_limit, self.page_offset, cd['sort'], cd['order'])

            if lst:
                user = _get_user()
                for item in lst:
                    item['user_name'] = user(item['user_id'])
            return lst, count

    @jsonresponse()
    def json(self):
        result, total = self.search()
        return {'data': result, "message": None, "pages": self.page_index, "success": True, "total": total}


class AuthUserLogDetailView(DetailView):
    template_name = "admin/pages/auth_user_log/detail.htm"

    def _get_user_name(self, user_id):
        service = UserModel()
        users = service.get_all()

    def search(self, pk, pks):
        service = AuthUserLogModel()
        d = service.get_detail(pk)

        user = _get_user()
        d['user_name'] = user(d['user_id'])
        return d
