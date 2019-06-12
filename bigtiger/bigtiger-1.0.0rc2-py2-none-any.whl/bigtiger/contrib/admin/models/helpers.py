# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from bigtiger.utils.choice import choice_wrap
from bigtiger.contrib.admin.models.auth_group import AuthGroupModel


@choice_wrap()
def get_auth_group_choice(*args, **kwargs):
    """角色信息"""
    service = AuthGroupModel()
    lst = service.get_all('name', 'asc')
    lst = [(item['id'], item['name']) for item in lst]
    return lst
