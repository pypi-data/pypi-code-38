# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from rest_framework.permissions import DjangoModelPermissions
__author__ = 'denishuang'

class DjangoModelPermissionsWithView(DjangoModelPermissions):
    perms_map = {}
    perms_map.update(DjangoModelPermissions.perms_map)
    perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']

    def get_required_permissions(self, method, model_cls):
        res = super(DjangoModelPermissionsWithView, self).get_required_permissions(method, model_cls)
        #print method, res
        return res